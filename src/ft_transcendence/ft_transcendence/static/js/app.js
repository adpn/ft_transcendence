function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const itemList = document.getElementById('item-list');
    const itemForm = document.getElementById('item-form');
    const itemName = document.getElementById('item-name');
    const itemDescription = document.getElementById('item-description');

    // Fetch items from the API
    function fetchItems() {
        fetch('/items/')
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
		var csrftoken = getCookie('csrftoken');
        fetch('/items/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
				'X-CSRFToken': csrftoken
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
