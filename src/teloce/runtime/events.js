export function emit(instance, name, ...args) {
  const handler = instance?.props?.[`on${name[0]?.toUpperCase()}${name.slice(1)}`];
  if (typeof handler === 'function') return handler(...args);
}
