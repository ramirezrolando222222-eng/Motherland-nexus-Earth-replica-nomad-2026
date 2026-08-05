/* Simple To-Do with localStorage
   Key: 'local_todos_v1'
*/
(() => {
  const STORAGE_KEY = 'local_todos_v1';

  // Elements
  const form = document.getElementById('todo-form');
  const input = document.getElementById('todo-input');
  const list = document.getElementById('todo-list');
  const remainingEl = document.getElementById('remaining');
  const filters = document.querySelectorAll('.filter');
  const clearCompletedBtn = document.getElementById('clear-completed');

  let todos = [];
  let filter = 'all';

  // Load & Save
  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      todos = raw ? JSON.parse(raw) : [];
    } catch (e) {
      console.error('Failed to load todos', e);
      todos = [];
    }
  }
  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
    } catch (e) {
      console.error('Failed to save todos', e);
    }
  }

  // Utilities
  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  // Render
  function render() {
    list.innerHTML = '';
    const visible = todos.filter(t => {
      if (filter === 'active') return !t.completed;
      if (filter === 'completed') return t.completed;
      return true;
    });

    for (const t of visible) {
      const li = document.createElement('li');
      li.className = 'todo-item' + (t.completed ? ' completed' : '');
      li.dataset.id = t.id;

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = t.completed;
      checkbox.setAttribute('aria-label', 'Mark complete');

      const content = document.createElement('div');
      content.className = 'content';
      content.textContent = t.text;
      content.title = 'Double-click to edit';

      const editBtn = document.createElement('button');
      editBtn.className = 'icon edit';
      editBtn.innerHTML = '✏️';
      editBtn.title = 'Edit';

      const delBtn = document.createElement('button');
      delBtn.className = 'icon delete';
      delBtn.innerHTML = '🗑️';
      delBtn.title = 'Delete';

      li.appendChild(checkbox);
      li.appendChild(content);
      li.appendChild(editBtn);
      li.appendChild(delBtn);
      list.appendChild(li);
    }

    updateStatus();
  }

  function updateStatus() {
    const remaining = todos.filter(t => !t.completed).length;
    remainingEl.textContent = String(remaining);
  }

  // Actions
  function addTask(text) {
    if (!text || !text.trim()) return;
    todos.unshift({ id: uid(), text: text.trim(), completed: false, created: Date.now() });
    save();
    render();
  }

  function toggleComplete(id) {
    const t = todos.find(x => x.id === id);
    if (!t) return;
    t.completed = !t.completed;
    save();
    render();
  }

  function deleteTask(id) {
    todos = todos.filter(x => x.id !== id);
    save();
    render();
  }

  function editTask(id, newText) {
    const t = todos.find(x => x.id === id);
    if (!t) return;
    t.text = newText.trim();
    save();
    render();
  }

  function clearCompleted() {
    todos = todos.filter(x => !x.completed);
    save();
    render();
  }

  // Events
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    addTask(input.value);
    input.value = '';
    input.focus();
  });

  // Delegate clicks in list (toggle, edit, delete)
  list.addEventListener('click', (e) => {
    const li = e.target.closest('li[data-id]');
    if (!li) return;
    const id = li.dataset.id;

    if (e.target.matches('input[type="checkbox"]')) {
      toggleComplete(id);
      return;
    }
    if (e.target.closest('.delete')) {
      deleteTask(id);
      return;
    }
    if (e.target.closest('.edit')) {
      // Replace content with input field
      const contentDiv = li.querySelector('.content');
      const prev = contentDiv.textContent;
      const inputEl = document.createElement('input');
      inputEl.type = 'text';
      inputEl.value = prev;
      inputEl.className = 'edit-input';
      contentDiv.replaceWith(inputEl);
      inputEl.focus();
      inputEl.select();

      function finishEdit(saveFlag) {
        if (saveFlag) editTask(id, inputEl.value);
        else render();
        inputEl.removeEventListener('blur', onBlur);
        inputEl.removeEventListener('keydown', onKey);
      }
      function onBlur() { finishEdit(true); }
      function onKey(ev) {
        if (ev.key === 'Enter') finishEdit(true);
        if (ev.key === 'Escape') finishEdit(false);
      }
      inputEl.addEventListener('blur', onBlur);
      inputEl.addEventListener('keydown', onKey);
      return;
    }
  });

  // Double-click to edit
  list.addEventListener('dblclick', (e) => {
    const li = e.target.closest('li[data-id]');
    if (!li) return;
    const editBtn = li.querySelector('.edit');
    if (editBtn) editBtn.click(); // reuse edit flow
  });

  // Filters
  filters.forEach(btn => {
    btn.addEventListener('click', () => {
      filters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filter = btn.dataset.filter;
      render();
    });
  });

  clearCompletedBtn.addEventListener('click', () => {
    clearCompleted();
  });

  // Init
  load();
  render();

  // Expose for debugging in console (optional)
  window._todos = {
    get: () => todos,
    add: addTask,
    save,
    load
  };
})();
