// ---------------------------------------------------------
// Student Management System - Client-side JS
// Handles live search and dashboard statistics.
// ---------------------------------------------------------

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function badgeClassForMarks(marks) {
    if (marks >= 85) return "badge-green";
    if (marks >= 70) return "badge-yellow";
    return "badge-red";
}

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

    tbody.innerHTML = students.map((student) => {
        const safeName = escapeHtml(student.name);
        const safeRollNo = escapeHtml(student.roll_no);
        const safeBranch = escapeHtml(student.branch);
        const badgeClass = badgeClassForMarks(Number(student.marks) || 0);
        const safeMarks = escapeHtml(student.marks);
        const confirmMessage = `Delete ${safeName}?`;

        return `
            <tr>
                <td>${escapeHtml(student.id)}</td>
                <td>${safeName}</td>
                <td>${safeRollNo}</td>
                <td>${safeBranch}</td>
                <td>${escapeHtml(student.semester)}</td>
                <td><span class="badge ${badgeClass}">${safeMarks}</span></td>
                <td class="actions">
                    <a href="/view/${escapeHtml(student.id)}" class="btn btn-sm btn-view">View</a>
                    <a href="/edit/${escapeHtml(student.id)}" class="btn btn-sm btn-edit">Edit</a>
                    <a href="/delete/${escapeHtml(student.id)}" class="btn btn-sm btn-delete" onclick="return confirm(${JSON.stringify(confirmMessage)});">Delete</a>
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
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    throw new Error(`Search request failed: ${response.status}`);
                }
                const data = await response.json();
                renderRows(data);
            } catch (error) {
                console.error("Search failed:", error);
            }
        }, 250);
    });
}

async function loadStats() {
    try {
        const response = await fetch("/api/stats");
        if (!response.ok) {
            throw new Error(`Stats request failed: ${response.status}`);
        }

        const data = await response.json();

        const avgEl = document.getElementById("avgMarks");
        const branchEl = document.getElementById("totalBranches");
        const totalEl = document.getElementById("totalStudents");

        if (avgEl) avgEl.textContent = Number(data.avg_marks ?? 0).toFixed(2);
        if (branchEl) branchEl.textContent = Array.isArray(data.branch_counts) ? data.branch_counts.length : 0;
        if (totalEl) totalEl.textContent = data.total ?? 0;
    } catch (error) {
        console.error("Failed to load stats:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setupSearch();
    loadStats();
});
