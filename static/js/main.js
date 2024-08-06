const video = document.getElementById('video');
const captureButton = document.getElementById('capture');
const recognizeButton = document.getElementById('recognize');
const progressBar = document.querySelector('.progress-bar');

// Helper function to play audio instruction
function playInstruction(instruction, callback) {
    const audio = new Audio(`/static/instructions/${instruction}.mp3`);
    audio.play();
    audio.onended = callback;
}

// Function to capture an image from the video stream
function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png');
}

// Update progress bar
function updateProgressBar(percentage) {
    progressBar.style.width = `${percentage}%`;
}

// Access the webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });

// Capture the photo and send to backend for recognition with liveness check
recognizeButton.addEventListener('click', () => {
    const instructions = ['blink_your_eyes', 'open_your_mouth'];
    let step = 0;

    function performLivenessCheck() {
        if (step < instructions.length) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += 1;
                updateProgressBar(progress);
                if (progress >= 100) {
                    clearInterval(interval);
                }
            }, 100); // 100 intervals to complete in 10 seconds

            console.log(`Playing instruction: ${instructions[step]}`);
            playInstruction(instructions[step], () => {
                const dataUrl = captureImage();
                console.log(`Captured image for: ${instructions[step]}`);
                fetch('/liveness_check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ instruction: instructions[step], image: dataUrl })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(`Liveness check result for ${instructions[step]}:`, data);
                    if (data.success) {
                        step++;
                        performLivenessCheck();
                    } else {
                        alert('Liveness check failed!');
                        clearInterval(interval);
                        updateProgressBar(0);
                    }
                });
            });
        } else {
            fetch('/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: captureImage() })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const audio = new Audio(data.greeting);
                    audio.play();
                    window.location.href = '/landing';
                } else {
                    alert('Face recognition failed!');
                }
            });
        }
    }

    performLivenessCheck();
});

captureButton.addEventListener('click', () => {
    const dataUrl = captureImage();
    fetch('/capture', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: dataUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Face captured successfully!');
        } else {
            alert('Face capture failed!');
        }
    });
});
