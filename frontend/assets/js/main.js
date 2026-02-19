// 1. Unified Course Data
const allCourses = [
    { id: 1, category: "Engineering", title: "Full-Stack Web Architecture", instructor: "David Miller", price: "199", img: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600" },
    { id: 2, category: "Data Science", title: "Applied AI & Neural Networks", instructor: "Dr. Elena Rossi", price: "249", img: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600" },
    { id: 3, category: "Design", title: "Advanced Product Psychology", instructor: "James Chen", price: "149", img: "https://images.unsplash.com/photo-1586717791821-3f44a563eb4c?w=600" },
    { id: 4, category: "Marketing", title: "Growth Hacking for Startups", instructor: "Sarah Jenkins", price: "129", img: "https://images.unsplash.com/photo-1533750516457-a7f992034fce?w=600" },
    { id: 5, category: "Engineering", title: "DevOps & CI/CD Pipelines", instructor: "Michael Scott", price: "179", img: "https://images.unsplash.com/photo-1618401471353-b98aade122f1?w=600" },
    { id: 6, category: "Data Science", title: "Big Data Visualization", instructor: "Sophia Wang", price: "210", img: "https://images.unsplash.com/photo-1551288049-bbbda5402742?w=600" }
];

// 2. Global State for Filters (used in courses.html)
let currentSearch = "";
let currentCategory = "All";

// 3. Function: Render Full Catalog (For courses.html)
function renderFullCatalog() {
    const grid = document.getElementById('courseList');
    if (!grid) return;

    const filtered = allCourses.filter(course => {
        const matchesSearch = course.title.toLowerCase().includes(currentSearch.toLowerCase()) || 
                              course.instructor.toLowerCase().includes(currentSearch.toLowerCase());
        const matchesCategory = currentCategory === "All" || course.category === currentCategory;
        return matchesSearch && matchesCategory;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `<div class="col-12 text-center py-5"><h4>No courses found</h4></div>`;
        return;
    }

    grid.innerHTML = filtered.map(course => `
        <div class="col-md-6 col-lg-4">
            <div class="course-card shadow-sm p-3 bg-white mb-4" style="border-radius: 24px;">
                <div class="card-img-container" style="height: 180px; overflow: hidden; border-radius: 18px;">
                    <img src="${course.img}" class="w-100 h-100" style="object-fit: cover;">
                </div>
                <div class="mt-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-3">${course.category}</span>
                        <span class="fw-bold text-dark">$${course.price}</span>
                    </div>
                    <h5 class="fw-bold mb-1">${course.title}</h5>
                    <p class="text-muted small mb-3">By ${course.instructor}</p>
                    <button class="btn btn-dark w-100 rounded-pill py-2 fw-bold" 
                        onclick="window.location.href='course-player.html?id=${course.id}'">
                        Enroll Now
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// 4. Function: Render Featured (For index.html)
function renderFeatured() {
    const featuredGrid = document.getElementById('courseGrid'); 
    if (!featuredGrid) return;

    const featured = allCourses.slice(0, 3);

    featuredGrid.innerHTML = featured.map(c => `
        <div class="col-md-4">
            <div class="course-card h-100 p-4 shadow-sm bg-white" style="border-radius: 24px;">
                <img src="${c.img}" class="img-fluid rounded-4 mb-3" style="height: 200px; width: 100%; object-fit: cover;">
                <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-3">${c.category}</span>
                <h5 class="fw-bold mt-3 mb-2">${c.title}</h5>
                <p class="text-muted small">Course by ${c.instructor}</p>
                <div class="d-flex justify-content-between align-items-center mt-4">
                    <span class="fw-bold fs-4">$${c.price}</span>
                    <button class="btn btn-outline-dark btn-sm rounded-pill px-3" 
                        onclick="window.location.href='course-player.html?id=${c.id}'">
                        Details
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// 5. Initialize Page Logic
document.addEventListener('DOMContentLoaded', () => {
    
    // Check if we are on index.html
    if (document.getElementById('courseGrid')) {
        renderFeatured();
    }

    // Check if we are on courses.html
    if (document.getElementById('courseList')) {
        renderFullCatalog();

        // Search Input Listener
        const searchInput = document.getElementById('courseSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                currentSearch = e.target.value;
                renderFullCatalog();
            });
        }

        // Category Filter Listener
        const filterBadges = document.querySelectorAll('.filter-badge');
        filterBadges.forEach(badge => {
            badge.addEventListener('click', function() {
                // Update active visual state
                filterBadges.forEach(b => {
                    b.classList.remove('active', 'btn-primary');
                    b.classList.add('btn-outline-primary');
                });
                this.classList.add('active', 'btn-primary');
                this.classList.remove('btn-outline-primary');

                // Update category and re-render
                currentCategory = this.getAttribute('data-category') || "All";
                renderFullCatalog();
            });
        });
    }
});