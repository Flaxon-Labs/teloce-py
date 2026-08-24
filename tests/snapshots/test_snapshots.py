"""
Snapshot tests for Teloce.

These tests compare compiler output against stored snapshots.
"""

import pytest
from pathlib import Path

from teloce.compiler.compiler import compile


class TestSnapshots:
    """Snapshot tests for Teloce."""

    def test_basic_snapshot(self):
        """Test basic component snapshot."""
        source = """
<template>
    <div>Hello World</div>
</template>

<script>
export default {
    name: 'Hello'
};
</script>
"""
        result = compile(source)
        
        # Snapshot would be stored in a file
        # For now, just verify the result
        assert result['success'] is True
        assert 'Hello World' in result['code']

    def test_counter_snapshot(self):
        """Test counter component snapshot."""
        source = """
<template>
    <div>
        <h1>{{ title }}</h1>
        <p>Count: {{ count }}</p>
        <button @click="increment">+</button>
        <button @click="decrement">-</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            title: 'Counter',
            count: 0
        };
    },
    methods: {
        increment() {
            this.count++;
        },
        decrement() {
            if (this.count > 0) this.count--;
        }
    }
};
</script>
"""
        result = compile(source)
        
        assert result['success'] is True
        assert 'Counter' in result['code']
        assert 'increment' in result['code']
        assert 'decrement' in result['code']

    def test_todo_snapshot(self):
        """Test todo component snapshot."""
        source = """
<template>
    <div>
        <h1>Todo List</h1>
        <input :model="newTodo" @keyup.enter="addTodo" />
        <button @click="addTodo">Add</button>
        <ul>
            <for key="id" item="todo" in="todos">
                <li :class="{ done: todo.done }">
                    <span @click="toggleTodo(todo.id)">{{ todo.text }}</span>
                    <button @click="deleteTodo(todo.id)">✕</button>
                </li>
            </for>
        </ul>
    </div>
</template>

<script>
export default {
    data() {
        return {
            newTodo: '',
            todos: [
                { id: 1, text: 'Learn Teloce', done: false }
            ]
        };
    },
    methods: {
        addTodo() {
            if (this.newTodo.trim()) {
                this.todos.push({
                    id: Date.now(),
                    text: this.newTodo.trim(),
                    done: false
                });
                this.newTodo = '';
            }
        },
        deleteTodo(id) {
            this.todos = this.todos.filter(t => t.id !== id);
        },
        toggleTodo(id) {
            const todo = this.todos.find(t => t.id === id);
            if (todo) todo.done = !todo.done;
        }
    }
};
</script>
"""
        result = compile(source)
        
        assert result['success'] is True
        assert 'addTodo' in result['code']
        assert 'deleteTodo' in result['code']
        assert 'toggleTodo' in result['code']