import { reactive } from './reactivity.js';

export function createComponent(definition, props = {}) {
  const state = reactive({ ...(definition.data ? definition.data() : {}), ...props });
  const instance = { definition, props, state, mounted: false };
  instance.mount = (target) => {
    if (typeof target === 'string') target = document.querySelector(target);
    if (!target) throw new Error('Teloce mount target was not found');
    const root = definition.render ? definition.render(state, props) : document.createDocumentFragment();
    target.replaceChildren(root);
    instance.mounted = true;
    definition.mounted?.call(state);
    return instance;
  };
  instance.unmount = () => { definition.unmounted?.call(state); instance.mounted = false; };
  return instance;
}

export function createApp(definition) {
  return { mount(target, props) { return createComponent(definition, props).mount(target); } };
}
