# Lesson 26: build a real CRUD app with `.vel` and Flask

This lesson demonstrates the production boundary: `.vel` owns the interactive
form and list, while Flask validates and stores data. The browser never calls
Python directly.

```html
<template>
  <form @submit.prevent="createTask">
    <input v-model="draft" aria-label="Task" />
    <button type="submit">Add</button>
  </form>
  <ul>
    <li v-for="task in tasks" :key="task.id">
      {{ task.title }}
      <button @click="removeTask(task.id)">Delete</button>
    </li>
  </ul>
</template>

<script>
export default {
  data() { return { draft: '', tasks: [] }; },
  async mounted() {
    this.tasks = await fetch('/api/tasks').then(response => response.json());
  },
  methods: {
    async createTask() {
      const title = this.draft.trim();
      if (!title) return;
      const response = await fetch('/api/tasks', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({title})
      });
      this.tasks = [...this.tasks, await response.json()];
      this.draft = '';
    }
  }
}
</script>
```

Use `examples/basic` as the executable baseline for the exact component API.
The Flask route must validate length, content type, authorization, and
persistence before returning JSON. Add browser tests for loading, creation,
validation, and deletion.
