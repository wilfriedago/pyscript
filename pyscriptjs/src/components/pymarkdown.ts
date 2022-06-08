import { BaseEvalElement } from './base';
import { addClasses, htmlDecode } from '../utils';
import { marked } from 'marked';

export class PyMarkdown extends BaseEvalElement {
    shadow: ShadowRoot;
    wrapper: HTMLElement;
    theme: string;
    widths: Array<string>;
    src: string;
    mount_name: string;
    constructor() {
        super();
    }

    connectedCallback() {
        this.checkId();
        this.src = htmlDecode(this.innerHTML);
        this.mount_name = this.id.split('-').join('_');
        this.innerHTML = '';

        const mainDiv = document.createElement('div');

        mainDiv.id = this.id;
        this.id = `${this.id}-container`;
        mainDiv.innerHTML = marked.parse(this.src)
        console.log(marked.parse(this.src))
        this.appendChild(mainDiv);
    }
}
