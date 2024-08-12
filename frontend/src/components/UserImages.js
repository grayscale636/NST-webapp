import React, { useState, useEffect } from 'react';
import axios from 'axios';

function UserImages() {
  const [images, setImages] = useState([]);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8000/user/images', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setImages(response.data);
      } catch (err) {
        console.error('Error fetching images:', err);
      }
    };

    fetchImages();
  }, []);

  return (
    <div>
      <h2>Your Images</h2>
      {images.map(image => (
        <div key={image.id}>
          <img src={`http://localhost:8000/outputs/${image.filename}`} alt={image.filename} />
          <p>{image.filename}</p>
        </div>
      ))}
    </div>
  );
}

export default UserImages;