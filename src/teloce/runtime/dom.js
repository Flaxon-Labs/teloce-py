export function createElement(tag, props = {}, children = []) {
  const element = document.createElement(tag);
  for (const [name, value] of Object.entries(props)) setAttribute(element, name, value);
  for (const child of children.flat()) if (child != null) element.append(child);
  return element;
}

export function setAttribute(element, name, value) {
  if (name === 'className') name = 'class';
  if (value === false || value == null) element.removeAttribute(name);
  else if (value === true) element.setAttribute(name, '');
  else element.setAttribute(name, String(value));
}

export function bindEvent(element, name, handler, options) {
  element.addEventListener(name, handler, options);
  return () => element.removeEventListener(name, handler, options);
}

export function bindEvents(element, bindings = []) {
  const unbind = bindings.map(binding => {
    const event = typeof binding === 'function' ? binding.event : binding.event || binding.name || binding.type;
    const handler = typeof binding === 'function' ? binding : binding.handler || binding.listener || binding.fn;
    if (!event || typeof handler !== 'function') return () => {};
    return bindEvent(element, event, handler, typeof binding === 'function' ? binding.options : binding.options);
  });
  return () => unbind.forEach(remove => remove());
}

export function createEventHandlerWithModifiers(element, name, handler) {
  const [eventName, ...modifiers] = String(name).split('.');
  const listener = event => {
    if (modifiers.includes('self') && event.target !== element) return;
    if (modifiers.includes('enter') && event.key !== 'Enter') return;
    if (modifiers.includes('esc') && event.key !== 'Escape') return;
    if (modifiers.includes('ctrl') && !event.ctrlKey) return;
    if (modifiers.includes('shift') && !event.shiftKey) return;
    if (modifiers.includes('alt') && !event.altKey) return;
    if (modifiers.includes('meta') && !event.metaKey) return;
    if (modifiers.includes('right') && event.button !== 2) return;
    if (modifiers.includes('middle') && event.button !== 1) return;
    if (modifiers.includes('left') && event.button !== 0) return;
    if (modifiers.includes('prevent')) event.preventDefault();
    if (modifiers.includes('stop')) event.stopPropagation();
    return handler(event);
  };
  listener.event = eventName;
  listener.options = {
    once: modifiers.includes('once'),
    capture: modifiers.includes('capture'),
    passive: modifiers.includes('passive'),
  };
  return listener;
}

export function createFor(container, source, renderItem, key = (_, index) => index) {
  const records = new Map();
  const read = value => typeof value === 'function' && value.__teloce_signal ? value() : value;
  const update = value => {
    const next = Array.from(read(value) || []);
    const active = new Set();
    const nodes = next.map((item, index) => {
      const id = key(item, index);
      const old = records.get(id);
      if (old) { old.item = item; old.index = index; active.add(id); return old.node; }
      const node = renderItem(item, index);
      records.set(id, { item, index, node });
      active.add(id);
      return node;
    });
    for (const id of records.keys()) if (!active.has(id)) records.delete(id);
    container.replaceChildren(...nodes.filter(Boolean));
  };
  update(source);
  const unsubscribe = source?.subscribe ? source.subscribe(update) : () => {};
  return { update, unmount() { unsubscribe?.(); records.clear(); container.replaceChildren(); } };
}

export function createIf(container, source, whenTrue, whenFalse = () => null) {
  const read = value => typeof value === 'function' && value.__teloce_signal ? value() : value;
  const update = value => {
    const node = (read(value) ? whenTrue : whenFalse)();
    container.replaceChildren(...(node == null ? [] : Array.isArray(node) ? node : [node]));
  };
  update(source);
  const unsubscribe = source?.subscribe ? source.subscribe(update) : () => {};
  return { update, unmount() { unsubscribe?.(); container.replaceChildren(); } };
}

export function createModel(element, signal) {
  const read = () => typeof signal === 'function' ? signal() : signal?.get?.();
  const write = value => typeof signal?.set === 'function' ? signal.set(value) : typeof signal === 'function' && signal.set ? signal.set(value) : undefined;
  const update = value => {
    const next = value === undefined ? read() : value;
    if (element.type === 'checkbox') element.checked = Boolean(next);
    else if (element.value !== String(next ?? '')) element.value = next ?? '';
  };
  const eventName = element.type === 'checkbox' || element.tagName === 'SELECT' ? 'change' : 'input';
  const listener = () => write(element.type === 'checkbox' ? element.checked : element.value);
  element.addEventListener(eventName, listener);
  update();
  const unsubscribe = signal?.subscribe ? signal.subscribe(update) : () => {};
  return { update, unmount() { unsubscribe?.(); element.removeEventListener(eventName, listener); } };
}

export function createClass(element, source) {
  const update = value => {
    const next = value === undefined ? (typeof source === 'function' ? source() : source?.get?.()) : value;
    if (typeof next === 'string') element.className = next;
    else if (Array.isArray(next)) element.className = next.filter(Boolean).join(' ');
    else if (next && typeof next === 'object') element.className = Object.entries(next).filter(([, enabled]) => enabled).map(([name]) => name).join(' ');
    else element.className = '';
  };
  update();
  const unsubscribe = source?.subscribe ? source.subscribe(update) : () => {};
  return { update, unmount() { unsubscribe?.(); } };
}

export function clear(element) { while (element.firstChild) element.firstChild.remove(); }
