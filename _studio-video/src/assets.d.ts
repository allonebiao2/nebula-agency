// Les cartes sont importées comme des modules : le bundler les remplace par une
// URL. Sans cette déclaration, TypeScript refuse `import carte from './x.png'`.
declare module '*.png' {
	const src: string;
	export default src;
}

declare module '*.jpg' {
	const src: string;
	export default src;
}

declare module '*.mp4' {
	const src: string;
	export default src;
}
