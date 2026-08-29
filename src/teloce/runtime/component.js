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

/** Create a component whose implementation is loaded only when mounted. */
export function defineAsyncComponent(loader, options = {}) {
  if (typeof loader !== 'function') throw new TypeError('defineAsyncComponent expects a loader function');
  let loaded;
  let loading;
  let current;
  let target;
  let props = {};
  const placeholder = options.loading ?? (() => document.createComment('teloce-async-loading'));
  const failure = options.error ?? (() => document.createComment('teloce-async-error'));
  const resolve = module => module?.default ?? module;
  const load = async () => {
    if (loaded) return loaded;
    if (!loading) loading = Promise.resolve(loader()).then(resolve).then(component => { loaded = component; return component; });
    return loading;
  };
  const instance = {
    get loaded() { return loaded; },
    async mount(nextTarget, nextProps = {}) {
      target = typeof nextTarget === 'string' ? document.querySelector(nextTarget) : nextTarget;
      if (!target) throw new Error('Teloce mount target was not found');
      props = nextProps;
      target.replaceChildren(typeof placeholder === 'function' ? placeholder() : placeholder);
      try {
        const definition = await load();
        current = definition?.mount ? definition.mount(target, props) : createComponent(definition, props).mount(target);
        return instance;
      } catch (error) {
        target.replaceChildren(typeof failure === 'function' ? failure(error) : failure);
        options.onError?.(error);
        throw error;
      }
    },
    updateProps(nextProps = {}) { props = nextProps; current?.updateProps?.(nextProps); },
    unmount() { current?.unmount?.(); current = undefined; target?.replaceChildren(); },
  };
  return instance;
}
