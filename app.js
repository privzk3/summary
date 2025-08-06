let documentText = '';

document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    document.getElementById('summaryBox').textContent = 'Summarizing...';
    document.getElementById('answerBox').textContent = 'No answer yet.';
    try {
        const response = await fetch('/summarize', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.summary) {
            document.getElementById('summaryBox').textContent = data.summary;
            documentText = data.document_text || data.summary;
        } else {
            document.getElementById('summaryBox').textContent = data.error || 'Failed to summarize.';
        }
    } catch (err) {
        document.getElementById('summaryBox').textContent = 'Error occurred.';
    }
});

document.getElementById('qaForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const question = document.getElementById('questionInput').value;
    if (!documentText) {
        document.getElementById('answerBox').textContent = 'Please summarize a document first.';
        return;
    }
    document.getElementById('answerBox').textContent = 'Thinking...';
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, document_text: documentText })
        });
        const data = await response.json();
        if (data.answer) {
            document.getElementById('answerBox').textContent = data.answer;
        } else {
            document.getElementById('answerBox').textContent = data.error || 'Failed to get answer.';
        }
    } catch (err) {
        document.getElementById('answerBox').textContent = 'Error occurred.';
    }
});