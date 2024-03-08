import { useMutation } from 'react-query';

interface UserProfileProps {
  initialImageUrl: string;
  userId: string;  // assuming you have some user identifier
}

const UserProfile: React.FC<UserProfileProps> = ({ initialImageUrl, userId }) => {
  const [imageUrl, setImageUrl] = useState<string>(initialImageUrl);
  
  const mutation = useMutation((file: File) => uploadProfilePicture(userId, file), {
    onSuccess: (data) => {
      // Update the local state with the new image URL
      setImageUrl(data.newImageUrl);
    }
  });

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      mutation.mutate(file);
    }
  };

  return (
    <div>
      <img src={imageUrl} alt="User Profile" onClick={onImageClick} style={{ cursor: 'pointer' }} />
      <input
        type="file"
        onChange={onFileChange}
        style={{ display: 'none' }}  // hide the input element
      />
      {mutation.isLoading && <p>Uploading...</p>}
      {mutation.isError && <p>Error: {mutation.error.message}</p>}
    </div>
  );
}

export default UserProfile;

import React, { useState, useRef } from 'react';

interface UserProfileProps {
  initialImageUrl: string;
  userId: string;  // assuming you have some user identifier
}

const UserProfile: React.FC<UserProfileProps> = ({ initialImageUrl, userId }) => {
  const [imageUrl, setImageUrl] = useState<string>(initialImageUrl);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const onImageClick = () => {
    fileInputRef.current?.click();
  };

  const onFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];

      const formData = new FormData();
      formData.append('image', file);
      formData.append('userId', userId);  // pass user identifier to the backend

      try {
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        setImageUrl(data.newImageUrl);
      } catch (error) {
        console.error('Error uploading the image:', error);
      }
    }
  };

  return (
    <div>
      <img src={imageUrl} alt="User Profile" onClick={onImageClick} style={{ cursor: 'pointer' }} />
      <input
        type="file"
        ref={fileInputRef}
        onChange={onFileChange}
        style={{ display: 'none' }}  // hide the input element
      />
    </div>
  );
}

export default UserProfile;

app.post('/api/upload', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send({ error: 'No file uploaded.' });
  }

  // Get the user ID from the request
  const userId = req.body.userId;
  if (!userId) {
    return res.status(400).send({ error: 'User ID is required.' });
  }

  const newImageUrl = `/uploads/${req.file.filename}`;

  try {
    // Update the user's profilePic using their user ID
    await User.findByIdAndUpdate(userId, { profilePic: newImageUrl });

    res.send({ newImageUrl });
  } catch (error) {
    console.error('Error updating user image:', error);
    res.status(500).send({ error: 'Internal Server Error' });
  }
});

const express = require('express');
const bodyParser = require('body-parser');
const cloudinary = require('cloudinary').v2;

const app = express();

// Cloudinary Configuration
cloudinary.config({
  cloud_name: 'YOUR_CLOUD_NAME',
  api_key: 'YOUR_API_KEY',
  api_secret: 'YOUR_API_SECRET'
});

app.use(bodyParser.json());

// Endpoint to generate signature
app.get('/generate_signature', (req, res) => {
  try {
    const timestamp = Math.round((new Date()).getTime() / 1000); // Unix timestamp in seconds

    // This is an example of parameters you might want for your upload; adjust accordingly.
    const params = {
      timestamp: timestamp,
      eager: 'w_400,h_300,c_pad|w_260,h_200,c_crop',
      public_id: 'my_sample_id'
    };

    // Generate signature
    const signature = cloudinary.utils.api_sign_request(params, 'YOUR_API_SECRET');

    res.json({
      signature: signature,
      timestamp: timestamp
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to generate signature' });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

import { Cloudinary } from "@cloudinary/url-gen";

async updateUserImg(img: File) {
  try {
    const token = getCookie("token");
    if (!token) {
      throw new Error("Token could not be retrieved!");
    }

    // Step 1: Retrieve signature and timestamp from backend
    const signResponse = await this.client.get("/api/users/gen_cld_sign", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const { signature, timestamp } = signResponse.data;

    // Step 2: Use the signature and timestamp to upload the image to Cloudinary
    const cld = new Cloudinary({ cloud: { cloudName: 'YOUR_CLOUD_NAME' } });
    const uploadResponse = await cloudinary.uploader.upload(img.path, {
      signature: signature,
      timestamp: timestamp,
      eager: "w_400,h_300,c_pad|w_260,h_200,c_crop",
      public_id: `users/avatars/${token}`  // This can be customized based on your needs
    });

    const imgUrl = uploadResponse.secure_url;
    if (!imgUrl) {
      throw new Error("Failed to get image URL from Cloudinary");
    }

    // Step 3: Send the retrieved URL to your backend
    const response = await this.client.post("/users/update/imgurl", {
      imgUrl: imgUrl
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    return response;
  } catch (err: any) {
    if (err.response?.data?.message) {
      err.message = err.response.data.message;
      throw err;
    }
    throw new Error("Unexpected error while updating user image!");
  }
}
