/**
 * Icon Utility for FlashFlow Frontend
 * Provides a unified interface for working with different icon packs
 */

class IconManager {
  constructor() {
    this.defaultPack = 'material-icons';
    this.packs = {
      'material-icons': {
        prefix: 'material-icons',
        getIcon: (name) => name
      },
      'font-awesome': {
        prefix: 'fas',
        getIcon: (name) => {
          // Map common icon names to Font Awesome classes
          const iconMap = {
            'home': 'fa-home',
            'dashboard': 'fa-tachometer-alt',
            'settings': 'fa-cog',
            'user': 'fa-user',
            'users': 'fa-users',
            'add': 'fa-plus',
            'edit': 'fa-edit',
            'delete': 'fa-trash',
            'save': 'fa-save',
            'cancel': 'fa-times',
            'search': 'fa-search',
            'filter': 'fa-filter',
            'sort': 'fa-sort',
            'menu': 'fa-bars',
            'close': 'fa-times',
            'check': 'fa-check',
            'error': 'fa-exclamation-circle',
            'info': 'fa-info-circle',
            'warning': 'fa-exclamation-triangle',
            'help': 'fa-question-circle',
            'arrow_back': 'fa-arrow-left',
            'arrow_forward': 'fa-arrow-right',
            'expand_more': 'fa-chevron-down',
            'expand_less': 'fa-chevron-up',
            'favorite': 'fa-heart',
            'share': 'fa-share',
            'download': 'fa-download',
            'upload': 'fa-upload',
            'print': 'fa-print',
            'email': 'fa-envelope',
            'phone': 'fa-phone',
            'location': 'fa-map-marker',
            'calendar': 'fa-calendar',
            'time': 'fa-clock',
            'lock': 'fa-lock',
            'unlock': 'fa-unlock',
            'visibility': 'fa-eye',
            'visibility_off': 'fa-eye-slash',
            'refresh': 'fa-sync',
            'undo': 'fa-undo',
            'redo': 'fa-redo'
          };
          return iconMap[name] || `fa-${name}`;
        }
      },
      'bootstrap-icons': {
        prefix: 'bi',
        getIcon: (name) => {
          // Map common icon names to Bootstrap Icons classes
          const iconMap = {
            'home': 'bi-house',
            'dashboard': 'bi-speedometer2',
            'settings': 'bi-gear',
            'user': 'bi-person',
            'users': 'bi-people',
            'add': 'bi-plus',
            'edit': 'bi-pencil',
            'delete': 'bi-trash',
            'save': 'bi-save',
            'cancel': 'bi-x',
            'search': 'bi-search',
            'filter': 'bi-funnel',
            'sort': 'bi-sort-down',
            'menu': 'bi-list',
            'close': 'bi-x',
            'check': 'bi-check',
            'error': 'bi-exclamation-circle',
            'info': 'bi-info-circle',
            'warning': 'bi-exclamation-triangle',
            'help': 'bi-question-circle',
            'arrow_back': 'bi-arrow-left',
            'arrow_forward': 'bi-arrow-right',
            'expand_more': 'bi-chevron-down',
            'expand_less': 'bi-chevron-up',
            'favorite': 'bi-heart',
            'share': 'bi-share',
            'download': 'bi-download',
            'upload': 'bi-upload',
            'print': 'bi-printer',
            'email': 'bi-envelope',
            'phone': 'bi-telephone',
            'location': 'bi-geo-alt',
            'calendar': 'bi-calendar',
            'time': 'bi-clock',
            'lock': 'bi-lock',
            'unlock': 'bi-unlock',
            'visibility': 'bi-eye',
            'visibility_off': 'bi-eye-slash',
            'refresh': 'bi-arrow-repeat',
            'undo': 'bi-arrow-counterclockwise',
            'redo': 'bi-arrow-clockwise'
          };
          return iconMap[name] || `bi-${name}`;
        }
      }
    };
  }

  /**
   * Get an icon class for rendering
   * @param {string} iconSpec - Icon specification (e.g., "home", "font-awesome:home")
   * @returns {string} CSS class for the icon
   */
  getIconClass(iconSpec) {
    if (!iconSpec) return '';
    
    // Handle pack:icon format
    if (iconSpec.includes(':')) {
      const [packName, iconName] = iconSpec.split(':');
      const pack = this.packs[packName];
      if (pack) {
        return `${pack.prefix} ${pack.getIcon(iconName)}`;
      }
    }
    
    // Use default pack
    const pack = this.packs[this.defaultPack];
    if (pack) {
      if (this.defaultPack === 'material-icons') {
        return pack.prefix;
      } else {
        return `${pack.prefix} ${pack.getIcon(iconSpec)}`;
      }
    }
    
    return '';
  }

  /**
   * Render an icon element
   * @param {string} iconSpec - Icon specification
   * @param {Object} props - Additional props for the icon element
   * @returns {JSX.Element} Icon element
   */
  renderIcon(iconSpec, props = {}) {
    if (!iconSpec) return null;
    
    const { className = '', ...restProps } = props;
    const iconClass = this.getIconClass(iconSpec);
    const fullClassName = `${iconClass} ${className}`.trim();
    
    // For Material Icons, the icon name is the content
    if (iconSpec.includes(':')) {
      const [packName, iconName] = iconSpec.split(':');
      if (packName === 'material-icons') {
        return React.createElement('i', {
          className: fullClassName,
          ...restProps
        }, iconName);
      }
    } else if (this.defaultPack === 'material-icons') {
      return React.createElement('i', {
        className: fullClassName,
        ...restProps
      }, iconSpec);
    }
    
    // For other icon packs, just use the class
    return React.createElement('i', {
      className: fullClassName,
      ...restProps
    });
  }

  /**
   * Set the default icon pack
   * @param {string} packName - Name of the icon pack
   */
  setDefaultPack(packName) {
    if (this.packs[packName]) {
      this.defaultPack = packName;
    }
  }

  /**
   * Get available icon packs
   * @returns {Array<string>} List of available icon pack names
   */
  getAvailablePacks() {
    return Object.keys(this.packs);
  }
}

// Create a global instance
const iconManager = new IconManager();

// Export for use in components
export default iconManager;

// Export individual functions for convenience
export const getIconClass = (iconSpec) => iconManager.getIconClass(iconSpec);
export const renderIcon = (iconSpec, props) => iconManager.renderIcon(iconSpec, props);
export const setDefaultIconPack = (packName) => iconManager.setDefaultPack(packName);
export const getAvailableIconPacks = () => iconManager.getAvailablePacks();