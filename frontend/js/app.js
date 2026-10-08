function isWholeNumberAtLeast(value, minimum) {
    const text = String(value).trim();
    return /^\\d+$/.test(text) && Number(text) >= minimum;
}

// ============================================================
// USER LOGIN
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const username =
            document.getElementById("username").value.trim();

        const password =
            document.getElementById("password").value;
            if (username === "") {
    alert("Please enter your username.");
    return;
}

if (password === "") {
    alert("Please enter your password.");
    return;
}

        try {

            const response = await fetch(
                "http://127.0.0.1:5000/api/login",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                }
            );

            const result = await response.json();

            if (response.ok) {

    sessionStorage.setItem("loggedIn", "true");
    sessionStorage.setItem("username", result.username);

    alert("Login successful!");

    window.location.href = "dashboard.html";

} else {

                alert(
                    result.error ||
                    "Invalid username or password."
                );
            }

        } catch (error) {

            alert(
                "Unable to connect to the server."
            );

            console.error(
                "Login error:",
                error
            );
        }

    });

}
// ============================================================
// PASSWORD TOGGLE - LOGIN
// ============================================================

function togglePassword() {

    const passwordInput =
        document.getElementById("password");

    const toggleButton =
        document.querySelector(".toggle-password");

    if (!passwordInput || !toggleButton) {
        return;
    }

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        toggleButton.textContent = "Hide";

    } else {

        passwordInput.type = "password";
        toggleButton.textContent = "Show";

    }
}


// ============================================================
// PASSWORD TOGGLE - REGISTER
// ============================================================

function toggleRegisterPassword() {

    const passwordInput =
        document.getElementById("registerPassword");

    const toggleButton =
        document.querySelector(".toggle-password");

    if (!passwordInput || !toggleButton) {
        return;
    }

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        toggleButton.textContent = "Hide";

    } else {

        passwordInput.type = "password";
        toggleButton.textContent = "Show";

    }
}


// ============================================================
// REGISTER FORM
// ============================================================

const registerForm =
    document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();

            const username =
                document
                    .getElementById("registerUsername")
                    .value
                    .trim();

            const email =
                document
                    .getElementById("registerEmail")
                    .value
                    .trim();

            const password =
                document
                    .getElementById("registerPassword")
                    .value;

            const confirmPassword =
                document
                    .getElementById("confirmPassword")
                    .value;


            // Frontend validation
            // Frontend validation
if (username === "") {
    alert("Please enter a username.");
    return;
}

if (email === "") {
    alert("Please enter an email address.");
    return;
}

if (!email.includes("@") || !email.includes(".")) {
    alert("Please enter a valid email address.");
    return;
}

if (password.length < 8) {
    alert(
        "Password must be at least 8 characters long."
    );
    return;
}

            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                return;
            }


            try {

                const response = await fetch(
                    "http://127.0.0.1:5000/api/register",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            username: username,
                            email: email,
                            password: password
                        })
                    }
                );


                const result = await response.json();


                if (response.ok) {

                    alert(
                        "Registration successful! You can now login."
                    );

                    registerForm.reset();

                    window.location.href = "login.html";

                } else {

                    alert(
                        "Registration failed: " +
                        (result.error || "Unknown error")
                    );
                }


            } catch (error) {

                alert(
                    "Unable to connect to the server."
                );

                console.error(
                    "Registration error:",
                    error
                );
            }

        }
    );

}
// ============================================================
// REPOSITORY SEARCH
// ============================================================

const repositorySearch =
    document.getElementById("repositorySearch");

if (repositorySearch) {

    repositorySearch.addEventListener(
        "input",
        function() {

            const searchText =
                repositorySearch.value.toLowerCase();

            const rows =
                document.querySelectorAll(
                    ".table-card tbody tr"
                );


            rows.forEach(function(row) {

                const firstCell =
                    row.querySelector("td");

                if (!firstCell) {
                    return;
                }

                const repositoryName =
                    firstCell.textContent.toLowerCase();


                if (
                    repositoryName.includes(searchText)
                ) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        }
    );

}


// ============================================================
// USER SEARCH
// ============================================================

const userSearch =
    document.getElementById("userSearch");

if (userSearch) {

    userSearch.addEventListener(
        "input",
        function() {

            const searchText =
                userSearch.value.toLowerCase();

            const rows =
                document.querySelectorAll(
                    ".table-card tbody tr"
                );


            rows.forEach(function(row) {

                const firstCell =
                    row.querySelector("td");

                if (!firstCell) {
                    return;
                }

                const username =
                    firstCell.textContent.toLowerCase();


                if (
                    username.includes(searchText)
                ) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        }
    );

}


// ============================================================
// ISSUE SEARCH + STATE FILTER
// ============================================================

const issueSearch =
    document.getElementById("issueSearch");

const issueStateFilter =
    document.getElementById("issueStateFilter");


if (issueSearch && issueStateFilter) {

    function filterIssues() {

        const searchText =
            issueSearch.value.toLowerCase();

        const selectedState =
            issueStateFilter.value.toLowerCase();


        const rows =
            document.querySelectorAll(
                ".table-card tbody tr"
            );


        rows.forEach(function(row) {

            const cells =
                row.querySelectorAll("td");


            if (cells.length < 3) {
                return;
            }


            const title =
                cells[1]
                    .textContent
                    .toLowerCase();

            const state =
                cells[2]
                    .textContent
                    .toLowerCase();


            const matchesSearch =
                title.includes(searchText);


            const matchesState =
                selectedState === "" ||
                state === selectedState;


            if (
                matchesSearch &&
                matchesState
            ) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    }


    issueSearch.addEventListener(
        "input",
        filterIssues
    );


    issueStateFilter.addEventListener(
        "change",
        filterIssues
    );

}


// ============================================================
// PULL REQUEST SEARCH + STATE FILTER
// ============================================================

const pullRequestSearch =
    document.getElementById(
        "pullRequestSearch"
    );

const pullRequestStateFilter =
    document.getElementById(
        "pullRequestStateFilter"
    );


if (
    pullRequestSearch &&
    pullRequestStateFilter
) {

    function filterPullRequests() {

        const searchText =
            pullRequestSearch.value.toLowerCase();

        const selectedState =
            pullRequestStateFilter.value.toLowerCase();


        const rows =
            document.querySelectorAll(
                ".table-card tbody tr"
            );


        rows.forEach(function(row) {

            const cells =
                row.querySelectorAll("td");


            if (cells.length < 3) {
                return;
            }


            const title =
                cells[1]
                    .textContent
                    .toLowerCase();

            const state =
                cells[2]
                    .textContent
                    .toLowerCase();


            const matchesSearch =
                title.includes(searchText);


            const matchesState =
                selectedState === "" ||
                state === selectedState;


            if (
                matchesSearch &&
                matchesState
            ) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    }


    pullRequestSearch.addEventListener(
        "input",
        filterPullRequests
    );


    pullRequestStateFilter.addEventListener(
        "change",
        filterPullRequests
    );

}


// ============================================================
// COMMIT SEARCH
// ============================================================

const commitSearch =
    document.getElementById("commitSearch");

if (commitSearch) {

    commitSearch.addEventListener(
        "input",
        function() {

            const searchText =
                commitSearch.value.toLowerCase();


            const rows =
                document.querySelectorAll(
                    ".table-card tbody tr"
                );


            rows.forEach(function(row) {

                const cells =
                    row.querySelectorAll("td");


                if (cells.length < 2) {
                    return;
                }


                const commitId =
                    cells[0]
                        .textContent
                        .toLowerCase();

                const commitMessage =
                    cells[1]
                        .textContent
                        .toLowerCase();


                if (
                    commitMessage.includes(
                        searchText
                    ) ||
                    commitId.includes(
                        searchText
                    )
                ) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        }
    );

}


// ============================================================
// LANGUAGE SEARCH
// ============================================================

const languageSearch =
    document.getElementById("languageSearch");

if (languageSearch) {

    languageSearch.addEventListener(
        "input",
        function() {

            const searchText =
                languageSearch.value.toLowerCase();


            const rows =
                document.querySelectorAll(
                    ".table-card tbody tr"
                );


            rows.forEach(function(row) {

                const cells =
                    row.querySelectorAll("td");


                if (cells.length < 2) {
                    return;
                }


                const language =
                    cells[1]
                        .textContent
                        .toLowerCase();


                if (
                    language.includes(searchText)
                ) {

                    row.style.display = "";

                } else {

                    row.style.display = "none";

                }

            });

        }
    );

}


// ============================================================
// LOAD USERS FROM FLASK API
// ============================================================

const usersTableBody =
    document.getElementById(
        "usersTableBody"
    );


if (usersTableBody) {

    fetch(
        "http://127.0.0.1:5000/api/users"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load users"
                );

            }

            return response.json();

        })

        .then(function(users) {

            usersTableBody.innerHTML = "";


            users.forEach(function(user) {

                const row =
                    document.createElement("tr");


                row.innerHTML = `
                    <td>${user.username || "-"}</td>
                    <td>${user.name || "-"}</td>
                    <td>${user.email || "-"}</td>
                    <td>${user.user_type || "-"}</td>
                    <td>${user.location || "-"}</td>
                    <td>${user.created_at || "-"}</td>
                `;


                usersTableBody.appendChild(row);

            });

        })

        .catch(function(error) {

            console.error(
                "Error loading users:",
                error
            );


            usersTableBody.innerHTML = `
                <tr>
                    <td colspan="6">
                        Unable to load users.
                    </td>
                </tr>
            `;

        });

}


// ============================================================
// LOAD REPOSITORIES FROM FLASK API
// ============================================================

const repositoriesTableBody =
    document.getElementById(
        "repositoriesTableBody"
    );


if (repositoriesTableBody) {

    fetch(
        "http://127.0.0.1:5000/api/repositories"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load repositories"
                );

            }

            return response.json();

        })

        .then(function(repositories) {

            repositoriesTableBody.innerHTML = "";


            repositories.forEach(
                function(repository) {

                    const row =
                        document.createElement("tr");


                    row.innerHTML = `
                        <td>${repository.name || "-"}</td>
                        <td>${repository.full_name || "-"}</td>
                        <td>${repository.stars ?? "-"}</td>
                        <td>${repository.forks ?? "-"}</td>
                        <td>${repository.open_issues ?? "-"}</td>
                        <td>${repository.created_at || "-"}</td>
                    `;


                    repositoriesTableBody.appendChild(
                        row
                    );

                }
            );

        })

        .catch(function(error) {

            console.error(
                "Error loading repositories:",
                error
            );


            repositoriesTableBody.innerHTML = `
                <tr>
                    <td colspan="6">
                        Unable to load repositories.
                    </td>
                </tr>
            `;

        });

}


// ============================================================
// LOAD ISSUES FROM FLASK API
// ============================================================

const issuesTableBody =
    document.getElementById(
        "issuesTableBody"
    );


if (issuesTableBody) {

    fetch(
        "http://127.0.0.1:5000/api/issues"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load issues"
                );

            }

            return response.json();

        })

        .then(function(issues) {

            issuesTableBody.innerHTML = "";


            issues.forEach(function(issue) {

                const row =
                    document.createElement("tr");


                row.innerHTML = `
                    <td>${issue.issue_id}</td>
                    <td>${issue.title || "-"}</td>
                    <td>${issue.state || "-"}</td>
                    <td>${issue.created_at || "-"}</td>
                    <td>${issue.closed_at || "-"}</td>
                    <td>${issue.creator_id || "-"}</td>
                    <td>${issue.repository_id || "-"}</td>
                `;


                issuesTableBody.appendChild(row);

            });

        })

        .catch(function(error) {

            console.error(
                "Error loading issues:",
                error
            );


            issuesTableBody.innerHTML = `
                <tr>
                    <td colspan="7">
                        Unable to load issues.
                    </td>
                </tr>
            `;

        });

}


// ============================================================
// LOAD PULL REQUESTS FROM FLASK API
// ============================================================

const pullRequestsTableBody =
    document.getElementById(
        "pullRequestsTableBody"
    );


if (pullRequestsTableBody) {

    fetch(
        "http://127.0.0.1:5000/api/pull-requests"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load pull requests"
                );

            }

            return response.json();

        })

        .then(function(pullRequests) {

            pullRequestsTableBody.innerHTML = "";


            pullRequests.forEach(
                function(pr) {

                    const row =
                        document.createElement("tr");


                    row.innerHTML = `
                        <td>${pr.pr_id}</td>
                        <td>${pr.title || "-"}</td>
                        <td>${pr.state || "-"}</td>
                        <td>${pr.created_at || "-"}</td>
                        <td>${pr.merged_at || "-"}</td>
                        <td>${pr.creator_id || "-"}</td>
                        <td>${pr.repository_id || "-"}</td>
                    `;


                    pullRequestsTableBody.appendChild(
                        row
                    );

                }
            );

        })

        .catch(function(error) {

            console.error(
                "Error loading pull requests:",
                error
            );


            pullRequestsTableBody.innerHTML = `
                <tr>
                    <td colspan="7">
                        Unable to load pull requests.
                    </td>
                </tr>
            `;

        });

}


// ============================================================
// LOAD COMMITS FROM FLASK API
// ============================================================

const commitsTableBody =
    document.getElementById(
        "commitsTableBody"
    );


if (commitsTableBody) {

    fetch(
        "http://127.0.0.1:5000/api/commits"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load commits"
                );

            }

            return response.json();

        })

        .then(function(commits) {

            commitsTableBody.innerHTML = "";


            commits.forEach(function(commit) {

                const row =
                    document.createElement("tr");


                row.innerHTML = `
                    <td>${commit.commit_id || "-"}</td>
                    <td>${commit.commit_message || "-"}</td>
                    <td>${commit.commit_date || "-"}</td>
                    <td>${commit.author_id || "-"}</td>
                    <td>${commit.repository_id || "-"}</td>
                `;


                commitsTableBody.appendChild(row);

            });

        })

        .catch(function(error) {

            console.error(
                "Error loading commits:",
                error
            );


            commitsTableBody.innerHTML = `
                <tr>
                    <td colspan="5">
                        Unable to load commits.
                    </td>
                </tr>
            `;

        });

}


// ============================================================
// LOAD LANGUAGES FROM FLASK API
// ============================================================

const languagesTableBody =
    document.getElementById(
        "languagesTableBody"
    );


if (languagesTableBody) {

    fetch(
        "http://127.0.0.1:5000/api/languages"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load languages"
                );

            }

            return response.json();

        })

        .then(function(languages) {

            languagesTableBody.innerHTML = "";


            languages.forEach(
                function(language) {

                    const row =
                        document.createElement("tr");


                    row.innerHTML = `
                        <td>${language.language_id}</td>
                        <td>${language.language_name || "-"}</td>
                    `;


                    languagesTableBody.appendChild(
                        row
                    );

                }
            );

        })

        .catch(function(error) {

            console.error(
                "Error loading languages:",
                error
            );


            languagesTableBody.innerHTML = `
                <tr>
                    <td colspan="2">
                        Unable to load languages.
                    </td>
                </tr>
            `;

        });

}


// ============================================================
// DASHBOARD STATISTICS
// ============================================================

const repositoryCount =
    document.getElementById(
        "repositoryCount"
    );

const userCount =
    document.getElementById(
        "userCount"
    );

const issueCount =
    document.getElementById(
        "issueCount"
    );

const pullRequestCount =
    document.getElementById(
        "pullRequestCount"
    );

const commitCount =
    document.getElementById(
        "commitCount"
    );


if (
    repositoryCount &&
    userCount &&
    issueCount &&
    pullRequestCount &&
    commitCount
) {

    fetch(
        "http://127.0.0.1:5000/api/dashboard-stats"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load dashboard statistics"
                );

            }

            return response.json();

        })

        .then(function(stats) {

            repositoryCount.textContent =
                stats.repositories;

            userCount.textContent =
                stats.users;

            issueCount.textContent =
                stats.issues;

            pullRequestCount.textContent =
                stats.pull_requests;

            commitCount.textContent =
                stats.commits;

        })

        .catch(function(error) {

            console.error(
                "Error loading dashboard statistics:",
                error
            );

        });

}
// ============================================================
// LOAD ANALYTICS FROM FLASK API
// ============================================================

const totalStars =
    document.getElementById("totalStars");

const totalForks =
    document.getElementById("totalForks");

const openIssues =
    document.getElementById("openIssues");

const closedIssues =
    document.getElementById("closedIssues");

const openPullRequests =
    document.getElementById("openPullRequests");

const mergedPullRequests =
    document.getElementById("mergedPullRequests");

const totalContributions =
    document.getElementById("totalContributions");


if (
    totalStars &&
    totalForks &&
    openIssues &&
    closedIssues &&
    openPullRequests &&
    mergedPullRequests &&
    totalContributions
) {

    fetch(
        "http://127.0.0.1:5000/api/analytics"
    )

        .then(function(response) {

            if (!response.ok) {

                throw new Error(
                    "Failed to load analytics"
                );

            }

            return response.json();

        })

        .then(function(analytics) {

            totalStars.textContent =
                analytics.total_stars;

            totalForks.textContent =
                analytics.total_forks;

            openIssues.textContent =
                analytics.open_issues;

            closedIssues.textContent =
                analytics.closed_issues;

            openPullRequests.textContent =
                analytics.open_pull_requests;

            mergedPullRequests.textContent =
                analytics.merged_pull_requests;

            totalContributions.textContent =
                analytics.total_contributions;

        })

        .catch(function(error) {

            console.error(
                "Error loading analytics:",
                error
            );

        });

}
// ================================
// PART C - ADD REPOSITORY
// ================================

const addRepositoryForm = document.getElementById("addRepositoryForm");

if (addRepositoryForm) {

    addRepositoryForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const repositoryData = {
            repository_id: Number(document.getElementById("addRepositoryId").value),
            name: document.getElementById("addName").value,
            full_name: document.getElementById("addFullName").value,
            description: document.getElementById("addDescription").value,
            stars: Number(document.getElementById("addStars").value),
            forks: Number(document.getElementById("addForks").value),
            open_issues: Number(document.getElementById("addOpenIssues").value),
            owner_id: Number(document.getElementById("addOwnerId").value)
        };
        // Validation
if (!isWholeNumberAtLeast(document.getElementById("addRepositoryId").value, 1)) {
    document.getElementById("addMessage").textContent =
        "Please enter a positive whole-number Repository ID.";
    return;
}

if (repositoryData.name.trim() === "") {
    document.getElementById("addMessage").textContent =
        "Please enter a repository name.";
    return;
}

if (repositoryData.full_name.trim() === "") {
    document.getElementById("addMessage").textContent =
        "Please enter the full repository name.";
    return;
}

if (!isWholeNumberAtLeast(document.getElementById("addOwnerId").value, 1)) {
    document.getElementById("addMessage").textContent =
        "Please enter a positive whole-number Owner ID.";
    return;
}

if (["addStars", "addForks", "addOpenIssues"].some((id) =>
    !isWholeNumberAtLeast(document.getElementById(id).value, 0)
)) {
    document.getElementById("addMessage").textContent =
        "Stars, forks and open issues must be whole numbers of zero or more.";
    return;
}

        try {

            const response = await fetch(
                "http://127.0.0.1:5000/api/repositories",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(repositoryData)
                }
            );

            const result = await response.json();

            const addMessage = document.getElementById("addMessage");

            if (response.ok) {

                addMessage.textContent =
                    "Repository added successfully!";

                addRepositoryForm.reset();

            } else {

                addMessage.textContent =
                    "Error: " + result.error;
            }

        } catch (error) {

            document.getElementById("addMessage").textContent =
                "Unable to connect to the server.";
        }

    });
}
// ================================
// PART C - FETCH REPOSITORY
// ================================

const fetchRepositoryForm = document.getElementById("fetchRepositoryForm");

if (fetchRepositoryForm) {

    fetchRepositoryForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const repositoryId =
            document.getElementById("fetchRepositoryId").value;

        const fetchResult =
            document.getElementById("fetchResult");

        if (!/^\d+$/.test(repositoryId.trim()) || Number(repositoryId) < 1) {
            fetchResult.textContent = "Enter a valid positive repository ID.";
            return;
        }

        try {

            const response = await fetch(
                `http://127.0.0.1:5000/api/repositories/${repositoryId}`
            );

            const result = await response.json();

            if (response.ok) {

                fetchResult.innerHTML = `
                    <h3>Repository Details</h3>
                    <p><strong>ID:</strong> ${result.repository_id}</p>
                    <p><strong>Name:</strong> ${result.name}</p>
                    <p><strong>Full Name:</strong> ${result.full_name}</p>
                    <p><strong>Description:</strong> ${result.description || "N/A"}</p>
                    <p><strong>Stars:</strong> ${result.stars}</p>
                    <p><strong>Forks:</strong> ${result.forks}</p>
                    <p><strong>Open Issues:</strong> ${result.open_issues}</p>
                    <p><strong>Owner ID:</strong> ${result.owner_id}</p>
                `;

            } else {

                fetchResult.innerHTML =
                    `<p>Repository not found.</p>`;
            }

        } catch (error) {

            fetchResult.innerHTML =
                `<p>Unable to connect to the server.</p>`;
        }

    });
}
// ================================
// PART C - SEARCH REPOSITORIES
// ================================
const searchButton = document.getElementById("searchButton");

if (searchButton) {
    searchButton.addEventListener("click", async function () {

        const searchName =
            document.getElementById("searchRepository").value.trim();

        const searchResults =
            document.getElementById("searchResults");

        if (searchName === "") {
            searchResults.innerHTML =
                "<p>Please enter a repository name.</p>";
            return;
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/api/repositories/search?name=${encodeURIComponent(searchName)}`
            );

            const repositories = await response.json();

            if (response.ok && repositories.length > 0) {

                let html = "<h3>Search Results</h3>";

                repositories.forEach(function (repo) {
                    html += `
                        <div>
                            <p><strong>ID:</strong> ${repo.repository_id}</p>
                            <p><strong>Name:</strong> ${repo.name}</p>
                            <p><strong>Full Name:</strong> ${repo.full_name}</p>
                            <p><strong>Stars:</strong> ${repo.stars}</p>
                            <p><strong>Forks:</strong> ${repo.forks}</p>
                            <p><strong>Open Issues:</strong> ${repo.open_issues}</p>
                            <p><strong>Owner ID:</strong> ${repo.owner_id}</p>
                            <hr>
                        </div>
                    `;
                });

                searchResults.innerHTML = html;

            } else {
                searchResults.innerHTML =
                    "<p>No repositories found.</p>";
            }

        } catch (error) {
            searchResults.innerHTML =
                "<p>Unable to connect to the server.</p>";
        }
    });
}
// ================================
// PART C - UPDATE REPOSITORY
// ================================
const updateRepositoryForm =
    document.getElementById("updateRepositoryForm");

if (updateRepositoryForm) {
    updateRepositoryForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const repositoryId =
            document.getElementById("updateRepositoryId").value;

        const updateData = {
            name: document.getElementById("updateName").value,
            stars: Number(document.getElementById("updateStars").value),
            forks: Number(document.getElementById("updateForks").value),
            open_issues: Number(
                document.getElementById("updateOpenIssues").value
            )
        };

        const updateMessage =
            document.getElementById("updateMessage");

        if (!/^\d+$/.test(repositoryId.trim()) || Number(repositoryId) < 1) {
            updateMessage.textContent = "Enter a valid positive repository ID.";
            return;
        }
        if (!updateData.name.trim()) {
            updateMessage.textContent = "Repository name is required.";
            return;
        }
        if (["updateStars", "updateForks", "updateOpenIssues"].some((id) =>
            !/^\d+$/.test(document.getElementById(id).value.trim())
        )) {
            updateMessage.textContent = "Stars, forks and open issues must be whole numbers of zero or more.";
            return;
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/api/repositories/${repositoryId}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(updateData)
                }
            );

            const result = await response.json();

            if (response.ok) {
                updateMessage.textContent =
                    "Repository updated successfully!";
                updateRepositoryForm.reset();
            } else {
                updateMessage.textContent =
                    "Error: " + result.error;
            }

        } catch (error) {
            updateMessage.textContent =
                "Unable to connect to the server.";
        }
    });
}
// ================================
// PART C - DELETE REPOSITORY
// ================================
const deleteRepositoryForm =
    document.getElementById("deleteRepositoryForm");

if (deleteRepositoryForm) {
    deleteRepositoryForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const repositoryId =
            document.getElementById("deleteRepositoryId").value;

        const deleteMessage =
            document.getElementById("deleteMessage");

        if (!/^\d+$/.test(repositoryId.trim()) || Number(repositoryId) < 1) {
            deleteMessage.textContent = "Enter a valid positive repository ID.";
            return;
        }
        if (!window.confirm("Delete repository " + repositoryId + "? This cannot be undone.")) {
            return;
        }

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/api/repositories/${repositoryId}`,
                {
                    method: "DELETE"
                }
            );

            const result = await response.json();

            if (response.ok) {
                deleteMessage.textContent =
                    "Repository deleted successfully!";
                deleteRepositoryForm.reset();
            } else {
                deleteMessage.textContent =
                    "Error: " + result.error;
            }

        } catch (error) {
            deleteMessage.textContent =
                "Unable to connect to the server.";
        }
    });
}
// ============================================================
// PAGE ACCESS PROTECTION
// ============================================================

const currentPage =
    window.location.pathname.split("/").pop();

const publicPages = [
    "login.html",
    "register.html"
];

if (!publicPages.includes(currentPage)) {

    const loggedIn =
        sessionStorage.getItem("loggedIn");

    if (loggedIn !== "true") {
        window.location.href = "login.html";
    }
}
// ============================================================
// LOGOUT
// ============================================================

const logoutLink =
    document.getElementById("logoutLink");

if (logoutLink) {

    logoutLink.addEventListener("click", function(event) {

        event.preventDefault();

        sessionStorage.removeItem("loggedIn");
        sessionStorage.removeItem("username");

        window.location.href = "login.html";
    });
}