import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { 
    getAuth, 
    signInWithEmailAndPassword, 
    createUserWithEmailAndPassword, 
    GoogleAuthProvider, 
    signInWithPopup, 
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
// ADDED FIRESTORE IMPORTS
import { getFirestore, doc, setDoc, getDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// 1. Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyD7I4uIk6ip0QGXTj7kqZ40x3DYGAlC48c",
    authDomain: "online-learning-1bb9e.firebaseapp.com",
    projectId: "online-learning-1bb9e",
    storageBucket: "online-learning-1bb9e.firebasestorage.app",
    messagingSenderId: "388461824734",
    appId: "1:388461824734:web:49127c9c4deb01d4fe504f",
    measurementId: "G-1N6PKH544J"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app); // INITIALIZED FIRESTORE
const provider = new GoogleAuthProvider();

// --- 2. AUTH OBSERVER (UPDATED TO PROTECT COURSE PLAYER) ---
onAuthStateChanged(auth, (user) => {
    const authArea = document.getElementById('navAuthArea');
    
    if (authArea) {
        if (user) {
            authArea.innerHTML = `
                <a href="dashboard.html" class="btn btn-primary px-4 shadow-sm">
                    <i class="fas fa-columns me-2"></i>Dashboard
                </a>`;
        } else {
            authArea.innerHTML = `
                <a href="auth.html" class="btn btn-outline-primary border-0 me-2">Log in</a>
                <a href="auth.html?mode=signup" class="btn btn-primary px-4 shadow-sm">Join for Free</a>`;
        }
    }

    // Protect Dashboard & Learning Pages
    const path = window.location.pathname.toLowerCase();
    const protectedPages = ["dashboard.html", "attendance.html", "course-player.html"];
    const isProtectedRoute = protectedPages.some(page => path.includes(page));
                               
    if (!user && isProtectedRoute) {
        window.location.href = "auth.html";
    }
});

// --- 3. PROGRESS & QUIZ TRACKING (NEW SECTION) ---
export async function saveUserProgress(userId, courseId, completedList, quizScore = null) {
    try {
        const data = {
            completed: completedList,
            lastUpdated: new Date()
        };
        if (quizScore !== null) data.quizScore = quizScore;

        await setDoc(doc(db, "userProgress", userId + "_" + courseId), data, { merge: true });
        console.log("Progress Saved to Firebase");
    } catch (err) {
        console.error("Error saving progress:", err);
    }
}

export async function getUserProgress(userId, courseId) {
    const docRef = doc(db, "userProgress", userId + "_" + courseId);
    const docSnap = await getDoc(docRef);
    return docSnap.exists() ? docSnap.data() : null;
}

// --- 4. SIGN UP LOGIC ---
const signupForm = document.getElementById('signupForm');
signupForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = signupForm.querySelector('#username')?.value;
    const email = signupForm.querySelector('input[type="email"]')?.value;
    const password = signupForm.querySelector('input[type="password"]')?.value;

    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        // We await the sync so the role is set before we move to dashboard
        await syncWithFlask(userCredential.user, name);
        window.location.href = "dashboard.html"; 
    } catch (error) {
        const feedback = document.getElementById('statusFeedback');
        if (feedback) feedback.innerText = "Signup Error: " + error.message;
    }
});

// --- 5. LOGIN LOGIC ---
const loginForm = document.getElementById('loginForm');
loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = loginForm.querySelector('input[type="email"]')?.value;
    const password = loginForm.querySelector('input[type="password"]')?.value;

    try {
        await signInWithEmailAndPassword(auth, email, password);
        window.location.href = "dashboard.html";
    } catch (error) {
        const feedback = document.getElementById('statusFeedback');
        if (feedback) feedback.innerText = "Invalid credentials.";
    }
});

// --- 6. GOOGLE SIGN-IN ---
document.getElementById('googleSignIn')?.addEventListener('click', async () => {
    try {
        provider.setCustomParameters({ prompt: 'select_account' });
        const result = await signInWithPopup(auth, provider);
        await syncWithFlask(result.user);
        window.location.href = "dashboard.html"; 
    } catch (error) {
        console.error("Google Auth Failed", error);
    }
});

// --- 7. LOGOUT ---
document.getElementById('logoutBtn')?.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
        await signOut(auth);
        localStorage.clear();
        window.location.replace("index.html");
    } catch (error) {
        console.error("Logout Error:", error);
    }
});

// --- 8. FLASK SYNC ---
async function syncWithFlask(user, customName = null) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/register-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uid: user.uid,
                email: user.email,
                username: customName || user.displayName || user.email.split('@')[0]
            })
        });
        
        if (!response.ok) throw new Error("Flask server error");
        
        const data = await response.json();
        localStorage.setItem('userRole', data.role);
    } catch (err) {
        console.error("Flask Sync Failed:", err);
        // Fallback: If Flask fails, we set a default role so the dashboard doesn't crash
        localStorage.setItem('userRole', 'student');
    }
}