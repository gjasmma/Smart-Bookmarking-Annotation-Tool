const apiUrl = 'http://localhost:5000';

// DOM Elements
const loginForm = document.getElementById('login-form');
const registerBtn = document.getElementById('register-btn');
const bookmarkSection = document.getElementById('bookmark-section');
const authSection = document.getElementById('auth-section');
const bookmarkForm = document.getElementById('bookmark-form');
const bookmarkList = document.getElementById('bookmark-list');
const searchQuery = document.getElementById('search-query');
const searchBtn = document.getElementById('search-btn');

let currentUserId = null;
let authToken = null;

// Handle Login
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  const res = await fetch(`${apiUrl}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();
  if (data.token) {
    authToken = data.token;
    currentUserId = data.userId;
    authSection.style.display = 'none';
    bookmarkSection.style.display = 'block';
    loadBookmarks();
  } else {
    alert('Invalid login credentials');
  }
});

// Handle Register
registerBtn.addEventListener('click', async () => {
  const username = prompt('Enter username:');
  const password = prompt('Enter password:');
  
  await fetch(`${apiUrl}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  alert('User registered! Now you can log in.');
});

// Handle Add Bookmark
bookmarkForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const url = document.getElementById('url').value;
  const title = document.getElementById('title').value;
  const tags = document.getElementById('tags').value.split(',');
  const notes = document.getElementById('notes').value;

  await fetch(`${apiUrl}/bookmarks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({ url, title, tags, notes })
  });

  loadBookmarks();
});

// Handle Search Bookmarks
searchBtn.addEventListener('click', async () => {
  const query = searchQuery.value;

  const res = await fetch(`${apiUrl}/search?query=${query}`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  const bookmarks = await res.json();
  
  renderBookmarks(bookmarks);
});

// Load all Bookmarks
async function loadBookmarks() {
  const res = await fetch(`${apiUrl}/bookmarks`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  const bookmarks = await res.json();

  renderBookmarks(bookmarks);
}

// Render Bookmarks to the UI
function renderBookmarks(bookmarks) {
  bookmarkList.innerHTML = '';
  bookmarks.forEach(bookmark => {
    const li = document.createElement('li');
    li.textContent = `${bookmark.title} - ${bookmark.url} - Tags: ${bookmark.tags.join(', ')}`;
    bookmarkList.appendChild(li);
  });
}