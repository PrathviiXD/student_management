// ---------------------------------------------------------
// Student Management System - Client-side JS
// Handles: live search (via /api/search) and dashboard stats (via /api/stats)
// ---------------------------------------------------------

function renderRows(students) {
    const tbody = document.getElementById("studentTableBody");
    const noResults = document.getElementById("noResults");
    if (!tbody) return;

    if (students.length === 0) {
        tbody.innerHTML = "";
        if (noResults) noResults.style.display = "block";
        return;
    }
    if (noResults) noResults.style.display = "none";

    tbody.innerHTML = students.map(s => {
        let badgeClass = "badge-red";
        if (s.marks >= 85) badgeClass = "badge-green";
        else if (s.marks >= 70) badgeClass = "badge-yellow";

        return `
            <tr>
                <td>${s.id}</td>
                <td>${s.name}</td>
                <td>${s.roll_no}</td>
                <td>${s.branch}</td>
                <td>${s.semester}</td>
                <td><span class="badge ${badgeClass}">${s.marks}</span></td>
                <td class="actions">
                    <a href="/view/${s.id}" class="btn btn-sm btn-view">View</a>
                    <a href="/edit/${s.id}" class="btn btn-sm btn-edit">Edit</a>
                    <a href="/delete/${s.id}" class="btn btn-sm btn-delete"
                       onclick="return confirm('Delete ${s.name}?');">Delete</a>
                </td>
            </tr>`;
    }).join("");
}

function setupSearch() {
    const searchBox = document.getElementById("searchBox");
    if (!searchBox) return;

    let debounceTimer;
    searchBox.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        debounceTimer = setTimeout(async () => {
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                renderRows(data);
            } catch (err) {
                console.error("Search failed:", err);
            }
        }, 250);
    });
}

async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();

        const avgEl = document.getElementById("avgMarks");
        const branchEl = document.getElementById("totalBranches");
        const totalEl = document.getElementById("totalStudents");

        if (avgEl) avgEl.textContent = data.avg_marks;
        if (branchEl) branchEl.textContent = data.branch_counts.length;
        if (totalEl) totalEl.textContent = data.total;
    } catch (err) {
        console.error("Failed to load stats:", err);
    }
}

document.addEventListener("DOMContentLoaded", setupSearch);
