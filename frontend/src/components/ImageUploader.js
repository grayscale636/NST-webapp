import React, { useState } from 'react';

function ImageUploader() {
    const [content, setContent] = useState(null);
    const [style, setStyle] = useState(null);
    const [generatedImage, setGeneratedImage] = useState(null);
    const [loading, setLoading] = useState(false); // State untuk loading

    const handleUpload = async () => {
        if (loading) return; // Jika sedang loading, jangan lakukan apa-apa

        const formData = new FormData();
        formData.append('content', content);
        formData.append('style', style);

        setLoading(true); // Set loading ke true saat mulai upload

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
        } finally {
            setLoading(false); // Set loading ke false setelah selesai
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
            <button onClick={handleUpload} disabled={loading}>Upload</button> {/* Nonaktifkan tombol saat loading */}
            {loading && <p>Loading...</p>} {/* Tampilkan loading indicator */}
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