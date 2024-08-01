document.addEventListener('DOMContentLoaded', function() {
    const itemList = document.getElementById('item-list');
    const itemForm = document.getElementById('item-form');
    const itemName = document.getElementById('item-name');
    const itemDescription = document.getElementById('item-description');

    // Fetch items from the API
    function fetchItems() {
        fetch('/pong/items/')
            .then(response => response.json())
            .then(data => {
                itemList.innerHTML = '';
                data.forEach(item => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${item.name}: ${item.description}`;
                    itemList.appendChild(listItem);
                });
            });
    }

    // Add item to the API
    itemForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const newItem = {
            name: itemName.value,
            description: itemDescription.value
        };

        fetch('/pong/items/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newItem)
        })
        .then(response => response.json())
        .then(data => {
            fetchItems(); // Refresh the item list
            itemForm.reset(); // Clear the form
        });
    });

    // Initial fetch
    fetchItems();
});