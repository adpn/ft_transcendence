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

// https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-da67bd33b552506b9d65c73ab83783a4f4d9c9c73c30db86ee1cb8f544f0f45f&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fauth42%2F&response_type=code

document.addEventListener("DOMContentLoaded", function() {
	var csrftoken = getCookie('csrftoken');
    login42button = document.getElementById('login-42auth');

    login42button.addEventListener('click', function(event) {
        event.preventDefault(); 
    
        window.location.href = "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-da67bd33b552506b9d65c73ab83783a4f4d9c9c73c30db86ee1cb8f544f0f45f&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fauth42%2F&response_type=code";
    });

});