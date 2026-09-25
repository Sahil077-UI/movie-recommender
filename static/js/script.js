const movieInput = document.getElementById("movieInput");
const recommendBtn = document.getElementById("recommendBtn");

const movieGrid = document.getElementById("movieGrid");
const resultsSection = document.getElementById("resultsSection");

const resultTitle = document.getElementById("resultTitle");
const errorMessage = document.getElementById("errorMessage");

const loading = document.getElementById("loading");


recommendBtn.addEventListener("click", getRecommendations);


movieInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        getRecommendations();
    }

});


async function getRecommendations() {

    const title = movieInput.value.trim();

    if (!title) {

        errorMessage.textContent =
            "Please enter a movie title.";

        return;
    }


    errorMessage.textContent = "";

    resultsSection.classList.add("hidden");

    loading.classList.remove("hidden");

    movieGrid.innerHTML = "";


    try {

        const response = await fetch(
            `/recommend?title=${encodeURIComponent(title)}`
        );

        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );

        }


        resultTitle.textContent =
            `Because you liked "${data.movie}"`;


        data.recommendations.forEach(movie => {

            createMovieCard(movie);

        });


        resultsSection.classList.remove("hidden");


    } catch (error) {

        errorMessage.textContent =
            error.message;

    } finally {

        loading.classList.add("hidden");

    }

}


function createMovieCard(movie) {

    const card = document.createElement("div");

    card.className = "movie-card";


    const poster = movie.poster
        ? `<img src="${movie.poster}" alt="${escapeHtml(movie.title)}">`
        : `<div class="no-poster">No Poster</div>`;


    const rating = movie.rating !== null
        ? `⭐ ${movie.rating.toFixed(1)}`
        : "No rating";


    const year = movie.release_date
        ? movie.release_date.substring(0, 4)
        : "N/A";


    card.innerHTML = `

        <div class="poster-container">
            ${poster}
        </div>

        <div class="movie-info">

            <h3>
                ${escapeHtml(movie.title)}
            </h3>

            <div class="movie-meta">

                <span>${year}</span>

                <span>${rating}</span>

            </div>

            <p class="movie-overview">
                ${escapeHtml(
                    movie.overview || "No overview available."
                )}
            </p>

        </div>
    `;


    movieGrid.appendChild(card);

}


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}