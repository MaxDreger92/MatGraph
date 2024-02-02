export const graphLayouts = [
    {
        name: "breadthfirst",
        spacingFactor: 175,
        directed: true,
    },
    {
        name: "concentric",
        minNodeSpacing: 50,
        spacingFactor: 3
    },
    {
        name: "grid",
        rows: 3,
    },
    {
        name: "fcose",
        animate: false,
        idealEdgeLength: 200,
        nodeSeparation: 2000,
        nodeRepulsion: 500_000,
        edgeElasticity: .45,
        numIter: 0,
        tile:false,
    },
]

