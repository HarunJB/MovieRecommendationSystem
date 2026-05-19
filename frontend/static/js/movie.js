let currentRating =
  parseFloat(document.getElementById("star-rating").dataset.current) || 0;

function highlightStars(value) {
  document.querySelectorAll(".star").forEach((star) => {
    star.classList.toggle("rated", parseInt(star.dataset.value) <= value);
  });
}

async function setRating(movieId, value) {
  highlightStars(value);
  currentRating = value;
  document.getElementById("rating-label").textContent =
    `You rated this ${Math.round(value)}/5`;
  await rateMovie(movieId, value, false);
}

document.querySelectorAll(".star").forEach((star) => {
  star.addEventListener("mouseover", () =>
    highlightStars(parseInt(star.dataset.value)),
  );
  star.addEventListener("mouseleave", () => highlightStars(currentRating));
});

highlightStars(currentRating);
