import React, { useState } from 'react';

function ImageUploader() {
    const [content, setContent] = useState(null);
    const [style, setStyle] = useState(null);
    const [generatedImage, setGeneratedImage] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleUpload = async () => {
        setIsLoading(true);
        setError(null);
        const formData = new FormData();
        formData.append('content', content);
        formData.append('style', style);
    
        try {
            const token = localStorage.getItem('token'); // Ambil token dari localStorage
            if (!token) {
                throw new Error('No authentication token found. Please login.');
            }

            const response = await fetch('http://localhost:8000/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${token}` // Tambahkan token ke header
                }
            });
    
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Unauthorized. Please login again.');
                }
                throw new Error('Failed to upload images');
            }
    
            const data = await response.json();
            console.log(data.message);
            await handleGetImage(data.generated_image_name);
        } catch (error) {
            console.error('Error:', error);
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleGetImage = async (imageName) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://localhost:8000/outputs/${imageName}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Image not found');
                } else if (response.status === 422) {
                    throw new Error('Unable to process the image request');
                } else {
                    throw new Error('Failed to get image');
                }
            }
            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);
            setGeneratedImage(imageUrl);
        } catch (error) {
            console.error('Error:', error);
            setError(error.message);
        }
    };

    return (
        <div>
            <input type="file" onChange={(e) => setContent(e.target.files[0])} />
            <input type="file" onChange={(e) => setStyle(e.target.files[0])} />
            <button onClick={handleUpload} disabled={isLoading}>
                {isLoading ? 'Processing...' : 'Upload'}
            </button>
            {isLoading && (
                <div>
                    <div className="loading-spinner"></div>
                    <p>Training images neural style transfer. Please wait...</p>
                </div>
            )}
            {error && <p style={{color: 'red'}}>{error}</p>}
            {generatedImage && !isLoading && (
                <div>
                    <h3>Generated Image:</h3>
                    <img src={generatedImage} alt="Generated" style={{ maxWidth: '100%', height: 'auto' }} />
                </div>
            )}
        </div>
    );
}

export default ImageUploader;