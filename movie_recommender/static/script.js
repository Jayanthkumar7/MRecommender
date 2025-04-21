async function getMovieRecommendations() {
    // Prevent default form submission

    // Get form values
    const movieTitle = document.getElementById("movie_name").value;
    const genre = document.getElementById("genre").value;
    const actors = document.getElementById("actor").value;
    const language = document.getElementById("language").value;
    const mood = document.getElementById("mood").value;

    try {
        // Send request to Flask backend
        const recommendation = await fetch("/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                movie_name: movieTitle,
                genre: genre,
                actor: actors,
                language: language,
                mood: mood
            }),
        });

        // Check if response is ok
        if (!recommendation.ok) {
            throw new Error("Failed to fetch recommendations");
        }

        const data = await recommendation.json();
        console.log('Hello World');
        console.log(data);
        const recommendations = data.recommendations; 

        if (recommendations.length === 0) {
            const res = document.querySelector(".results");
            res.innerHTML = "<h2>No recommendations found</h2>";
            return;
        }
        const res = document.querySelector(".results");
        res.style.display = "block";
        const cont = document.querySelector(".container");
        cont.style.marginTop = "180px";
        cont.style.height = "100vh";
        const movie_list = document.querySelector(".movie-list");

        recommendations.forEach((movie) => {
            movie_list.innerHTML += `
                                <div class="movie-item" id = "movie-item">
                                <img src="${movie[1]}" alt="Movie 1" class="movie-poster">
                                <h2>${movie[0]}</h2>    
                                </div>
            `
        });
    } catch (error) {
        console.error("An error occurred:", error);
    }



}