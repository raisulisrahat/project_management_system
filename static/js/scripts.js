// Ensure the DOM is fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add keyup event listener to the search input field
    document.getElementById('search-input').addEventListener('keyup', function() {
        const query = this.value;

        // Perform the search only if the query has more than 2 characters
        if (query.length > 2) {
            fetch(`/search/?q=${query}`)  // Send the query to your search endpoint
                .then(response => response.json())
                .then(data => {
                    let resultsDiv = document.getElementById('search-results');
                    resultsDiv.innerHTML = '';  // Clear previous results

                    if (data.results) {
                        // Display Projects if available
                        if (data.results.project.length > 0) {
                            resultsDiv.innerHTML += '<h3>Projects</h3><ul>';
                            data.results.project.forEach(project => {
                                resultsDiv.innerHTML += `<li>${project.title} (${project.label})</li>`;
                            });
                            resultsDiv.innerHTML += '</ul>';
                        }

                        // Display Tasks if available
                        if (data.results.task.length > 0) {
                            resultsDiv.innerHTML += '<h3>Tasks</h3><ul>';
                            data.results.task.forEach(task => {
                                resultsDiv.innerHTML += `<li>${task.summary} (${task.unique_id})</li>`;
                            });
                            resultsDiv.innerHTML += '</ul>';
                        }

                        // Display Issues if available
                        if (data.results.issue.length > 0) {
                            resultsDiv.innerHTML += '<h3>Issues</h3><ul>';
                            data.results.issue.forEach(issue => {
                                resultsDiv.innerHTML += `<li>${issue.title}</li>`;
                            });
                            resultsDiv.innerHTML += '</ul>';
                        }

                        // Display Departments if available
                        if (data.results.department.length > 0) {
                            resultsDiv.innerHTML += '<h3>Departments</h3><ul>';
                            data.results.department.forEach(department => {
                                resultsDiv.innerHTML += `<li>${department.department_name}</li>`;
                            });
                            resultsDiv.innerHTML += '</ul>';
                        }
                    } else {
                        resultsDiv.innerHTML = '<p>No results found.</p>';
                    }
                });
        } else {
            document.getElementById('search-results').innerHTML = '';  // Clear results if the query is too short
        }
    });
});


function toggle2FA(value) {
    if (value === 'enable') {
        document.getElementById('2fa-modal').style.display = 'block';
    } else {
        close2FAModal();
    }
}

function close2FAModal() {
    document.getElementById('2fa-modal').style.display = 'none';
}