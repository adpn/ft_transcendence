document.addEventListener("DOMContentLoaded", function() {
    var testElements = document.getElementsByClassName('test');
    
    // Get all buttons by class
    var transformButtons = document.getElementsByClassName("transform-btn");
    var biggerButtons = document.getElementsByClassName("bigger-btn");
    var deleteButtons = document.getElementsByClassName("delete-btn");

    // Add event listeners to all transform buttons
    for (var i = 0; i < transformButtons.length; i++) {
        transformButtons[i].addEventListener("click", function() {
            transformContent();
        });
    }

    // Add event listeners to all bigger buttons
    for (var i = 0; i < biggerButtons.length; i++) {
        biggerButtons[i].addEventListener("click", function() {
            makeBigger();
        });
    }

    // Add event listeners to all delete buttons
    for (var i = 0; i < deleteButtons.length; i++) {
        deleteButtons[i].addEventListener("click", function() {
            deleteContent();
        });
    }

    // Function to transform the content of the divs
    function transformContent() {
        for (var i = 0; i < testElements.length; i++) {
            testElements[i].innerHTML = "Transformed!";
        }
    }

    // Function to make the text bigger
    function makeBigger() {
        for (var i = 0; i < testElements.length; i++) {
            testElements[i].style.fontSize = "2em";
        }
    }

    // Function to delete the content of the divs
    function deleteContent() {
        for (var i = 0; i < testElements.length; i++) {
            testElements[i].innerHTML = "";
        }
    }
});

// Example functions
function handleHomeClick() {
    console.log('Home button clicked');
    // Your logic here
}

function handleGamesClick() {
    console.log('Games button clicked');
    // Your logic here
}

function handleLoginClick() {
    console.log('Log in button clicked');
    // Your logic here
}

function handleSignInClick() {
    console.log('Sign in button clicked');
    // Your logic here
}
