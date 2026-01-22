const form = document.getElementById('uploadForm');
const resultText = document.getElementById('result');
const imageTag = document.getElementById('uploadedImage');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    const response = await fetch('/predict', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    if (data.result) {
        resultText.textContent = `Prediction: ${data.result} (Confidence: ${data.confidence}%)`;
        imageTag.src = data.image_url;
        imageTag.style.display = 'block';
    } else {
        resultText.textContent = 'Something went wrong!';
    }
});
