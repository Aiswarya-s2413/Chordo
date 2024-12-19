//  to change the main product image when thumbnails are clicked
function changeImage(src) {
    document.getElementById('main-product-image').src = src;
}
// Select main image and its container
const mainImageContainer = document.querySelector('.main-image-container');
const mainImage = document.querySelector('#main-product-image');

// Mousemove Event: Zoom in and follow the pointer
mainImageContainer.addEventListener('mousemove', (e) => {
    const rect = mainImageContainer.getBoundingClientRect(); // Container size and position
    const x = ((e.clientX - rect.left) / rect.width) * 100; // X position in percentage
    const y = ((e.clientY - rect.top) / rect.height) * 100; // Y position in percentage

    mainImage.style.transformOrigin = `${x}% ${y}%`; // Set zoom focus to cursor position
    mainImage.style.transform = 'scale(2)'; // Zoom in
});

// Mouseleave Event: Reset zoom
mainImageContainer.addEventListener('mouseleave', () => {
    mainImage.style.transform = 'scale(1)'; // Reset zoom
    mainImage.style.transformOrigin = 'center center'; // Reset origin
});


//for variant color in color box
document.querySelectorAll('.color-box').forEach(function(colorBox) {
    var bgColor = colorBox.getAttribute('data-bg-color');
    if (bgColor) {
        colorBox.style.backgroundColor = bgColor;
    }
});

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if element exists before trying to add event listener
    const mainImageContainer = document.querySelector('.main-image-container');
    if (mainImageContainer) {
        // Only add event listeners if the element exists
        mainImageContainer.addEventListener('click', function() {
            // Your existing image click handling code
        });
    }
}); 
