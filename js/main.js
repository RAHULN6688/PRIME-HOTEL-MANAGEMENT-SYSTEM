$(function() {

  var siteSticky = function() {
		$(".js-sticky-header").sticky({topSpacing:0});
	};
	siteSticky();

	var siteMenuClone = function() {

		$('.js-clone-nav').each(function() {
			var $this = $(this);
			$this.clone().attr('class', 'site-nav-wrap').appendTo('.site-mobile-menu-body');
		});


		setTimeout(function() {
			
			var counter = 0;
      $('.site-mobile-menu .has-children').each(function(){
        var $this = $(this);
        
        $this.prepend('<span class="arrow-collapse collapsed">');

        $this.find('.arrow-collapse').attr({
          'data-toggle' : 'collapse',
          'data-target' : '#collapseItem' + counter,
        });

        $this.find('> ul').attr({
          'class' : 'collapse',
          'id' : 'collapseItem' + counter,
        });

        counter++;

      });

    }, 1000);

		$('body').on('click', '.arrow-collapse', function(e) {
      var $this = $(this);
      if ( $this.closest('li').find('.collapse').hasClass('show') ) {
        $this.removeClass('active');
      } else {
        $this.addClass('active');
      }
      e.preventDefault();  
      
    });

		$(window).resize(function() {
			var $this = $(this),
				w = $this.width();

			if ( w > 768 ) {
				if ( $('body').hasClass('offcanvas-menu') ) {
					$('body').removeClass('offcanvas-menu');
				}
			}
		})

		$('body').on('click', '.js-menu-toggle', function(e) {
			var $this = $(this);
			e.preventDefault();

			if ( $('body').hasClass('offcanvas-menu') ) {
				$('body').removeClass('offcanvas-menu');
				$this.removeClass('active');
			} else {
				$('body').addClass('offcanvas-menu');
				$this.addClass('active');
			}
		}) 

		// click outisde offcanvas
		$(document).mouseup(function(e) {
	    var container = $(".site-mobile-menu");
	    if (!container.is(e.target) && container.has(e.target).length === 0) {
	      if ( $('body').hasClass('offcanvas-menu') ) {
					$('body').removeClass('offcanvas-menu');
				}
	    }
		});
	}; 
	siteMenuClone();

});

    document.addEventListener('DOMContentLoaded', function () {
        var usernameElement = document.getElementById('username');
        var logoutButton = document.getElementById('logout');

        if (usernameElement.innerText.trim() !== '') {
            // User is logged in, show logout button
            logoutButton.style.display = 'inline';
        } else {
            // User is not logged in, hide logout button
            logoutButton.style.display = 'none';
        }
    });

    function logout() {
        window.location.href = '/logout';
    }

	$(document).ready(function () {
		// Add smooth scrolling to all links
		$("a").on('click', function (event) {
		  if (this.hash !== "") {
			event.preventDefault();
  
			// Store hash
			var hash = this.hash;
  
			// Using jQuery's animate() method to add smooth page scroll
			$('html, body').animate({
			  scrollTop: $(hash).offset().top
			}, 800, function () {
			  // Add hash (#) to URL when done scrolling (default click behavior)
			  window.location.hash = hash;
			});
		  }
		});
  
		// Toggle Back-to-Top Button Visibility
		var backToTopButton = $("#back-to-top");
  
		$(window).scroll(function () {
		  if ($(this).scrollTop() > 100) {
			backToTopButton.fadeIn();
		  } else {
			backToTopButton.fadeOut();
		  }
		});
	  });

  function resetForm() {
    document.getElementById('contactForm').reset();
  }

  // Optional: You can add additional form validation or customization here

  // Add an event listener to the form for the 'submit' event
  document.getElementById('contactForm').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent the default form submission

    // Optionally, you can add form validation here

    // Get the form data
    const formData = new FormData(this);

    // Send the form data to Formspree using Fetch API
    fetch('https://formspree.io/f/mnqevakw', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        // Optionally, you can handle the response from Formspree here
        console.log('Formspree Response:', data);

        // Optionally, you can redirect or show a success message here
        alert('Form submitted successfully!');
        resetForm();
      })
      .catch(error => {
        console.error('Error submitting form:', error);
        // Optionally, you can handle errors here
        alert('Error submitting form. Please try again later.');
      });
  });
