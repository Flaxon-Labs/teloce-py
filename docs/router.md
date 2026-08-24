# Router

The generated router supports route parameters, optional parameters, wildcards, query strings, navigation, history, and reactive route state. Keep authorization on the Python server; browser routing is not access control.

Use the router for client view state and normal Python endpoints for data. Test navigation and refresh behavior in a real browser.

## Route concepts

The generated router supports routes such as:

```text
/                 home
/users/:id        required parameter
/posts/:slug?     optional parameter
/docs/*           wildcard path
```

Query values are separate from path parameters. A route can read the current
path, params, query, and full URL, then navigate with push, replace, back,
forward, or a numeric history step.

The router is a browser view mechanism, not a security mechanism. The Python
server must validate the user and authorize every data request, including
requests made after client-side navigation. Configure server fallback routes
if refreshing a client route should return the application shell.
