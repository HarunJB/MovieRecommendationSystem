let currentPage = 1;
let totalPages = 1;
let allRatings = [];

document.addEventListener("DOMContentLoaded", async () => {
  await loadStats();
  await loadRatings(1);

  // Search on Enter key
  document
    .getElementById("profile-search")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") searchMovies();
    });
});

async function loadStats() {
  try {
    const data = await apiFetch("/api/movies/user-stats");
    document.getElementById("total-ratings").textContent = data.total_ratings;
    document.getElementById("avg-rating").textContent = data.avg_rating + " ★";
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

async function loadRatings(page) {
  try {
    const data = await apiFetch(`/api/movies/user-ratings?page=${page}`);
    currentPage = data.current_page;
    totalPages = data.pages;

    if (page === 1) {
      allRatings = data.ratings;
    } else {
      allRatings = [...allRatings, ...data.ratings];
    }

    renderRatings(data.ratings, page);
  } catch (err) {
    document.getElementById("ratings-list").innerHTML =
      `<p class="text-danger">Failed to load ratings.</p>`;
  }
}

function renderRatings(ratings, page) {
  const container = document.getElementById("ratings-list");

  if (ratings.length === 0 && page === 1) {
    container.innerHTML = `<p class="text-muted">You haven't rated any movies yet.</p>`;
    return;
  }

  const items = ratings
    .map((m) => {
      const poster = m.poster_path
        ? `<img src="https://image.tmdb.org/t/p/w45${m.poster_path}" class="rounded me-3" style="width:45px;height:65px;object-fit:cover;">`
        : `<div class="me-3 d-flex align-items-center justify-content-center rounded bg-secondary" style="width:45px;height:65px;"><i class="bi bi-film text-muted"></i></div>`;

      const stars = Array.from(
        { length: 5 },
        (_, i) =>
          `<i class="bi bi-star-fill" style="color: ${i < m.user_rating ? "#f5c518" : "#444"}; font-size:0.75rem;"></i>`,
      ).join("");

      return `
        <div class="d-flex align-items-center py-2 border-bottom border-secondary rating-item"
             onclick="window.location='/movie/${m.movie_id}?from=profile'" style="cursor:pointer;">
            ${poster}
            <div class="flex-grow-1">
                <div class="fw-bold">${m.title}</div>
                <small class="text-muted">${m.release_year || ""}</small>
            </div>
            <div class="text-end">
                <div>${stars}</div>
                <small class="text-muted">${m.user_rating}/5</small>
            </div>
        </div>`;
    })
    .join("");

  if (page === 1) {
    container.innerHTML = items;
  } else {
    // Remove show more button before appending
    const btn = document.getElementById("show-more-btn");
    if (btn) btn.remove();
    container.insertAdjacentHTML("beforeend", items);
  }

  if (currentPage < totalPages) {
    container.insertAdjacentHTML(
      "beforeend",
      `
            <div id="show-more-btn" class="text-center mt-3">
                <button class="btn btn-outline-secondary btn-sm px-4" onclick="loadRatings(${currentPage + 1})">
                    Show More
                </button>
            </div>
        `,
    );
  }
}

async function searchMovies() {
  const query = document.getElementById("profile-search").value.trim();
  if (!query) return;

  const data = await apiFetch(
    `/api/movies/search?q=${encodeURIComponent(query)}`,
  );
  const container = document.getElementById("search-results");

  if (!data.length) {
    container.innerHTML = `<p class="text-muted small mt-2">No movies found.</p>`;
    return;
  }

  container.innerHTML = data
    .map((m) => {
      const poster = m.poster_path
        ? `<img src="https://image.tmdb.org/t/p/w45${m.poster_path}" class="rounded me-2" style="width:40px;height:58px;object-fit:cover;">`
        : `<div class="me-2 d-flex align-items-center justify-content-center rounded bg-secondary" style="width:40px;height:58px;"><i class="bi bi-film text-muted small"></i></div>`;

      return `
        <div class="col-12">
            <div class="d-flex align-items-center py-2 border-bottom border-secondary search-result-item"
                 onclick="window.location='/movie/${m.movie_id}?from=profile'" style="cursor:pointer;">
                ${poster}
                <div class="flex-grow-1">
                    <span class="fw-bold">${m.title}</span>
                    <small class="text-muted ms-2">${m.release_year || ""}</small>
                </div>
                <i class="bi bi-chevron-right text-muted"></i>
            </div>
        </div>`;
    })
    .join("");
}

function sortRatings() {
  const sort = document.getElementById("sort-select").value;
  let sorted = [...allRatings];

  if (sort === "highest") {
    sorted.sort((a, b) => b.user_rating - a.user_rating);
  } else if (sort === "lowest") {
    sorted.sort((a, b) => a.user_rating - b.user_rating);
  } else {
    sorted.sort((a, b) => new Date(b.rated_at) - new Date(a.rated_at));
  }

  const container = document.getElementById("ratings-list");
  const btn = document.getElementById("show-more-btn");
  if (btn) btn.remove();
  container.innerHTML = sorted
    .map((m) => {
      const poster = m.poster_path
        ? `<img src="https://image.tmdb.org/t/p/w45${m.poster_path}" class="rounded me-3" style="width:45px;height:65px;object-fit:cover;">`
        : `<div class="me-3 d-flex align-items-center justify-content-center rounded bg-secondary" style="width:45px;height:65px;"><i class="bi bi-film text-muted"></i></div>`;

      const stars = Array.from(
        { length: 5 },
        (_, i) =>
          `<i class="bi bi-star-fill" style="color: ${i < m.user_rating ? "#f5c518" : "#444"}; font-size:0.75rem;"></i>`,
      ).join("");

      return `
        <div class="d-flex align-items-center py-2 border-bottom border-secondary rating-item"
             onclick="window.location='/movie/${m.movie_id}?from=profile'" style="cursor:pointer;">
            ${poster}
            <div class="flex-grow-1">
                <div class="fw-bold">${m.title}</div>
                <small class="text-muted">${m.release_year || ""}</small>
            </div>
            <div class="text-end">
                <div>${stars}</div>
                <small class="text-muted">${m.user_rating}/5</small>
            </div>
        </div>`;
    })
    .join("");
}
