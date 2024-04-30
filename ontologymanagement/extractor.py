import multiprocessing
import time
from multiprocessing import Queue, Process
from queue import Empty
from datetime import datetime

from django.contrib.admin import SimpleListFilter
from django_cron import Schedule
from django.db import connection
from neomodel import db, StringProperty, IntegerProperty, DateTimeProperty

EXTRACTOR_STATE_TODO = 'todo'
EXTRACTOR_STATE_RETRY = 'retry'
EXTRACTOR_STATE_DONE = 'done'
EXTRACTOR_STATE_DISABLED = 'disabled'
EXTRACTOR_STATE_FAILED = 'failed'
EXTRACTOR_STATES = {
    EXTRACTOR_STATE_TODO: 'TODO',
    EXTRACTOR_STATE_RETRY: 'RETRY',
    EXTRACTOR_STATE_DONE: 'DONE',
    EXTRACTOR_STATE_DISABLED: 'DISABLED',
    EXTRACTOR_STATE_FAILED: 'FAILED'
}

EXTRACTOR_STATUS_SUCCESS = 'success'
EXTRACTOR_STATUS_FAILED = 'failed'


class ExtractorStateModelMixin:

    extractor_state = StringProperty(choices=EXTRACTOR_STATES, default=EXTRACTOR_STATE_TODO)
    extractor_tries = IntegerProperty(default=0)
    extractor_reason = StringProperty(required=False) # fail reason
    extractor_date = DateTimeProperty(required=False)

    def set_extractor_state(self, state, reason=None, date=datetime.now(), tries=None):
        self.extractor_state = state
        self.extractor_date = date
        if tries is not None:
            self.extractor_tries = tries
        if reason:
            self.extractor_reason = reason


class ExtractorStateFilter(SimpleListFilter):

    title = "Extraktionsstatus"
    parameter_name = "extractor_state"

    def lookups(self, request, model_admin):
        return EXTRACTOR_STATES.items()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(extractor_state=self.value())
        return queryset


class ExtractorCronJobMixin:

    schedule = Schedule(run_every_mins=1)
    extractor_class = None
    item_class = None

    LIMIT_PER_RUN = 200
    PARALLEL_PROCESSES = 8
    EXTRACTION_RETRIES = 1

    def __init__(self, *args, **kwargs):
        self.extractor = None
        super().__init__(*args, **kwargs)

    def process_queue(self, input_queue, result_queue, extractor):
        while True:
            try:
                result_queue.put(
                    extractor.fetch(
                        input_queue.get_nowait()
                    )
                )
            except Empty:
                break
        return True

    def should_run(self):
        return True

    def fetch_items(self):
        raise NotImplementedError

    def on_extraction_successful(self, item):
        pass

    def on_extraction_failed(self, item):
        pass

    def run(self):

        if not self.should_run():
            return

        with db.read_transaction:
            items = self.fetch_items()

            if not len(items):
                return

            # make sure this happens in read transaction as well - extractor might load embeddings
            self.extractor = self.extractor_class()

        # important since the default method on MacOS is spawned, which does not work with django
        multiprocessing.set_start_method('fork')

        input_queue = Queue()
        result_queue = Queue()
        processes = []

        for item in items:
            if self.extractor.is_input_suitable(item):
                input_queue.put(item)
            else:
                item = self.item_class.nodes.get(uid=item['uid'])
                item.set_extractor_state(
                    EXTRACTOR_STATE_DISABLED,
                    reason='not suitable'
                )
                item.save()

        for w in range(self.PARALLEL_PROCESSES):
            p = Process(target=self.process_queue, args=(input_queue, result_queue, self.extractor))
            processes.append(p)
            p.start()

        try:

            # store results in db
            last_run = False
            while not last_run:

                # make sure all processes have ended if queues are empty
                if result_queue.empty() and input_queue.empty():
                    last_run = True
                    for p in processes:
                        p.join()

                while not result_queue.empty():
                    with db.write_transaction:

                        output = result_queue.get_nowait()
                        item = self.item_class.nodes.get(uid=output["input"]["uid"])

                        tries = item.extractor_tries + 1

                        if output['status'] == EXTRACTOR_STATUS_SUCCESS:

                            self.extractor.save(output, item)
                            self.on_extraction_successful(item)

                            item.set_extractor_state(EXTRACTOR_STATE_DONE, tries=tries, )

                        elif output['status'] == EXTRACTOR_STATUS_FAILED:

                            if item.extractor_tries < self.EXTRACTION_RETRIES+1:
                                item.set_extractor_state(EXTRACTOR_STATE_RETRY, tries=tries, reason=output['reason'])
                            else:
                                item.set_extractor_state(EXTRACTOR_STATE_FAILED, tries=tries, reason=output['reason'])
                                self.on_extraction_failed(item)

                        else:
                            raise ValueError(f'unknown status: '+output['status'])

                        item.save()

                time.sleep(.5)


        except:

            # important to make sure to kill all fetching processes if the db writer fails
            for p in processes:
                p.kill()
                p.join()

            raise


class DataExtractor:

    # is executed by cron job in read transaction (to load embeddings and stuff)
    def __init__(self):
        pass

    # classmethod so this method can be used before the instance is initialized
    # (we don't need to load embeddings if no items are to be extracted)
    @classmethod
    def is_input_suitable(cls, input):
        return True

    # executed in write transaction
    def save(self, output, item):
        raise NotImplementedError

    def fetch(self, item):
        raise NotImplementedError