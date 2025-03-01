document.getElementById('search-input').addEventListener('keyup', function() {
    const query = this.value;

    if (query.length > 2) {  // Start searching only when 3 or more characters are typed
        fetch(`/search/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                let resultsDiv = document.getElementById('search-results');
                resultsDiv.innerHTML = '';  // Clear previous results

                if (data.results) {
                    // Display Projects
                    if (data.results.project.length > 0) {
                        resultsDiv.innerHTML += '<h3>Projects</h3><ul>';
                        data.results.project.forEach(project => {
                            resultsDiv.innerHTML += `<li>${project.title} (${project.label})</li>`;
                        });
                        resultsDiv.innerHTML += '</ul>';
                    }

                    // Display Tasks
                    if (data.results.task.length > 0) {
                        resultsDiv.innerHTML += '<h3>Tasks</h3><ul>';
                        data.results.task.forEach(task => {
                            resultsDiv.innerHTML += `<li>${task.summary} (${task.unique_id})</li>`;
                        });
                        resultsDiv.innerHTML += '</ul>';
                    }

                    // Display Issues
                    if (data.results.issue.length > 0) {
                        resultsDiv.innerHTML += '<h3>Issues</h3><ul>';
                        data.results.issue.forEach(issue => {
                            resultsDiv.innerHTML += `<li>${issue.title}</li>`;
                        });
                        resultsDiv.innerHTML += '</ul>';
                    }

                    // Display Departments
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
        document.getElementById('search-results').innerHTML = '';  // Clear results if query is too short
    }
});