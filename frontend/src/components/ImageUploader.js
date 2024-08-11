import React, { useState } from 'react';

function ImageUploader() {
    const [content, setContent] = useState(null);
    const [style, setStyle] = useState(null);
    const [generatedImage, setGeneratedImage] = useState(null);

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('content', content);
        formData.append('style', style);

        try {
            const response = await fetch('http://localhost:8000/upload/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Gagal mengupload gambar');
            }

            const data = await response.json();
            console.log(data.message);
            handleGetImage(data.generated_image_name);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const handleGetImage = async (imageName) => {
        try {
            const response = await fetch(`http://localhost:8000/outputs/${imageName}`);
            if (!response.ok) {
                throw new Error('Gagal mendapatkan gambar');
            }
            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);
            setGeneratedImage(imageUrl); // Simpan URL gambar yang diambil
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <input type="file" onChange={(e) => setContent(e.target.files[0])} />
            <input type="file" onChange={(e) => setStyle(e.target.files[0])} />
            <button onClick={handleUpload}>Upload</button>
            {generatedImage && (
                <div>
                    <h3>Gambar yang Dihasilkan:</h3>
                    <img src={generatedImage} alt="Generated" style={{ maxWidth: '100%', height: 'auto' }} />
                </div>
            )}
        </div>
    );
}

export default ImageUploader;