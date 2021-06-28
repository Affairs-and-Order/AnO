window.addEventListener("load", parallax)
window.addEventListener("scroll", parallax)

function parallax() {

    function getPosition(item) {

        let top = (item.getBoundingClientRect().top / window.innerHeight * 100).toFixed(0)

        return top
    }

    let itemsToParallax = document.getElementsByClassName("parallaxify")

    for (let item of itemsToParallax) {

        if (!item.dataset.speedMultiplier) {

            item.dataset.speedMultiplier = "0.7"
        }

        item.style.transform = "translateY(" + getPosition(item) * item.dataset.speedMultiplier + "px)"
    }

    let imagesToParallax = document.getElementsByClassName("parallaxifyBg")

    for (let item of imagesToParallax) {

        function getPosition(item) {

            let top = (item.getBoundingClientRect().top / window.innerHeight * 100).toFixed(0)

            return top
        }

        if (!item.dataset.speedMultiplier) {

            item.dataset.speedMultiplier = "3"
        }

        item.style.backgroundAttachment = "fixed"
        item.style.backgroundPositionY = getPosition(item) * item.dataset.speedMultiplier + "px"
    }
}