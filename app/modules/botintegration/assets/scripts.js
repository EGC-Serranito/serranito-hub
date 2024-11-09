function toggleChildren(nodeId) {
    const childrenDiv = document.getElementById(`children-${nodeId}`);
    const toggleButton = childrenDiv.previousElementSibling;
    childrenDiv.classList.toggle('show');
    toggleButton.innerText = childrenDiv.classList.contains('show') ? '▼' : '►';
}

// Función para fusionar los árboles
async function mergeTrees(nodeId) {
    try {
        const response = await fetch(`/api/nodes/merge/${nodeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: {{ user_id }} })
        });
        if (!response.ok) {
            throw new Error(`Error al fusionar nodos: ${response.statusText}`);
        }
        const result = await response.json();
        alert('Fusión completada exitosamente!');
    } catch (error) {
        console.error('Error merging trees:', error);
        alert('Error al realizar la fusión.');
    }
}