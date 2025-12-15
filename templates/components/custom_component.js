/**
 * Custom Component Template
 * This is an example of a custom template you can add to FlashFlow
 */

class CustomComponent {
  constructor(props) {
    this.props = props || {};
  }

  render() {
    const { title, content, className = '' } = this.props;
    
    return `
      <div class="custom-component ${className}">
        <h2 class="custom-component-title">${title}</h2>
        <div class="custom-component-content">${content}</div>
      </div>
    `;
  }
}

export default CustomComponent;