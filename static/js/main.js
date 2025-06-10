document.addEventListener('DOMContentLoaded', function () {
    // 提取所有品质和角色选项
    const costumes = [];

    // 等待DOM完全加载后再获取所有卡片元素
    setTimeout(() => {
        // 获取所有卡片元素
        const cardElements = document.querySelectorAll('div[data-id]');

        // 遍历所有卡片元素并添加到costumes数组
        cardElements.forEach(element => {
            const id = element.dataset.id;
            const character = element.querySelector('.text-base.font-semibold').textContent;
            const quality_name = element.querySelector('.text-sm.text-gray-500').textContent;

            costumes.push({
                id: id,
                quality_name: quality_name,
                character: character,
                element: element
            });
        });

        // 初始化筛选下拉菜单
        initializeFilters();
    }, 100);

    // 初始化筛选状态
    const filters = {
        quality: [],
        character: []
    };

    // 获取DOM元素
    const qualityTags = document.getElementById('qualityTags');
    const qualityDropdown = document.getElementById('qualityDropdown');
    const qualitySearch = document.getElementById('qualitySearch');
    const qualityAll = document.getElementById('qualityAll');

    const characterTags = document.getElementById('characterTags');
    const characterDropdown = document.getElementById('characterDropdown');
    const characterSearch = document.getElementById('characterSearch');
    const characterAll = document.getElementById('characterAll');

    // 初始化筛选器函数
    function initializeFilters() {

        // 填充品质下拉菜单
        const qualitySet = new Set();
        costumes.forEach(c => qualitySet.add(c.quality_name));
        const qualityOptions = Array.from(qualitySet);

        qualityOptions.forEach(quality => {
            const optionId = `quality-${quality.replace(/\s+/g, '-')}`;
            const optionDiv = document.createElement('div');
            optionDiv.className = 'flex items-center gap-2 p-2 hover:bg-primary-50 rounded-lg cursor-pointer transition-colors duration-200';
            optionDiv.dataset.value = quality;
            optionDiv.innerHTML = `
            <input type="checkbox" id="${optionId}" class="h-5 w-5 text-primary-600 rounded focus:ring-primary-500">
            <label for="${optionId}" class="cursor-pointer flex-1 text-gray-800">${quality}</label>
        `;
            qualityDropdown.querySelector('div').appendChild(optionDiv);

            // 添加点击事件
            optionDiv.addEventListener('click', function (e) {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;

                if (checkbox.checked) {
                    addFilter('quality', quality);
                } else {
                    removeFilter('quality', quality);
                }

                e.stopPropagation();
            });
        });

        // 填充角色下拉菜单
        const characterSet = new Set();
        costumes.forEach(c => characterSet.add(c.character));
        const characterOptions = Array.from(characterSet);

        characterOptions.forEach(character => {
            const optionId = `character-${character.replace(/\s+/g, '-')}`;
            const optionDiv = document.createElement('div');
            optionDiv.className = 'flex items-center gap-2 p-2 hover:bg-primary-50 rounded-lg cursor-pointer transition-colors duration-200';
            optionDiv.dataset.value = character;
            optionDiv.innerHTML = `
            <input type="checkbox" id="${optionId}" class="h-5 w-5 text-primary-600 rounded focus:ring-primary-500">
            <label for="${optionId}" class="cursor-pointer flex-1 text-gray-800">${character}</label>
        `;
            characterDropdown.querySelector('div').appendChild(optionDiv);

            // 添加点击事件
            optionDiv.addEventListener('click', function (e) {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;

                if (checkbox.checked) {
                    addFilter('character', character);
                } else {
                    removeFilter('character', character);
                }

                e.stopPropagation();
            });
        });

        // 全选/取消全选品质
        qualityAll.parentElement.addEventListener('click', function (e) {
            const isChecked = !qualityAll.checked;
            qualityAll.checked = isChecked;

            const checkboxes = qualityDropdown.querySelectorAll('input[type="checkbox"]:not(#qualityAll)');
            checkboxes.forEach(cb => {
                cb.checked = isChecked;
            });

            if (isChecked) {
                // 全选
                filters.quality = [...qualityOptions];
            } else {
                // 取消全选
                filters.quality = [];
            }

            updateTags('quality');
            applyFilters();
            e.stopPropagation();
        });

        // 全选/取消全选角色
        characterAll.parentElement.addEventListener('click', function (e) {
            const isChecked = !characterAll.checked;
            characterAll.checked = isChecked;

            const checkboxes = characterDropdown.querySelectorAll('input[type="checkbox"]:not(#characterAll)');
            checkboxes.forEach(cb => {
                cb.checked = isChecked;
            });

            if (isChecked) {
                // 全选
                filters.character = [...characterOptions];
            } else {
                // 取消全选
                filters.character = [];
            }

            updateTags('character');
            applyFilters();
            e.stopPropagation();
        });

        // 点击输入框显示下拉菜单
        qualitySearch.addEventListener('click', function (e) {
            qualityDropdown.classList.remove('hidden');
            characterDropdown.classList.add('hidden');
            e.stopPropagation();
        });

        qualityTags.addEventListener('click', function (e) {
            qualityDropdown.classList.remove('hidden');
            characterDropdown.classList.add('hidden');
            qualitySearch.focus();
            e.stopPropagation();
        });

        characterSearch.addEventListener('click', function (e) {
            characterDropdown.classList.remove('hidden');
            qualityDropdown.classList.add('hidden');
            e.stopPropagation();
        });

        characterTags.addEventListener('click', function (e) {
            characterDropdown.classList.remove('hidden');
            qualityDropdown.classList.add('hidden');
            characterSearch.focus();
            e.stopPropagation();
        });

        // 点击页面其他地方关闭下拉菜单
        document.addEventListener('click', function () {
            qualityDropdown.classList.add('hidden');
            characterDropdown.classList.add('hidden');
        });

        // 搜索功能
        qualitySearch.addEventListener('input', function () {
            const searchText = this.value.toLowerCase();
            const options = qualityDropdown.querySelectorAll('div[data-value]:not([data-value=""])');

            options.forEach(option => {
                const value = option.dataset.value.toLowerCase();
                if (value.includes(searchText)) {
                    option.style.display = 'flex';
                } else {
                    option.style.display = 'none';
                }
            });
        });

        characterSearch.addEventListener('input', function () {
            const searchText = this.value.toLowerCase();
            const options = characterDropdown.querySelectorAll('div[data-value]:not([data-value=""])');

            options.forEach(option => {
                const value = option.dataset.value.toLowerCase();
                if (value.includes(searchText)) {
                    option.style.display = 'flex';
                } else {
                    option.style.display = 'none';
                }
            });
        });

        // 添加筛选条件
        function addFilter(type, value) {
            if (!filters[type].includes(value)) {
                filters[type].push(value);
                updateTags(type);
                applyFilters();
            }
        }

        // 移除筛选条件
        function removeFilter(type, value) {
            const index = filters[type].indexOf(value);
            if (index !== -1) {
                filters[type].splice(index, 1);
                updateTags(type);
                applyFilters();
            }
        }

        // 更新标签显示
        function updateTags(type) {
            const container = type === 'quality' ? qualityTags : characterTags;
            const search = type === 'quality' ? qualitySearch : characterSearch;

            // 移除现有标签
            const existingTags = container.querySelectorAll('.filter-tag');
            existingTags.forEach(tag => tag.remove());

            // 添加新标签
            filters[type].forEach(value => {
                const tag = document.createElement('div');
                tag.className = 'filter-tag flex items-center bg-primary-500 text-white text-sm rounded-full px-3 py-1';
                tag.innerHTML = `
                        <span class="mr-1">${value}</span>
                        <button type="button" class="text-white hover:text-gray-200 focus:outline-none" data-value="${value}">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    `;

                // 添加删除事件
                tag.querySelector('button').addEventListener('click', function (e) {
                    removeFilter(type, this.dataset.value);
                    e.stopPropagation();
                });

                container.insertBefore(tag, search);
            });

            // 更新全选复选框状态
            const allCheckbox = type === 'quality' ? qualityAll : characterAll;
            const options = type === 'quality' ? qualityOptions : characterOptions;

            if (filters[type].length === options.length) {
                allCheckbox.checked = true;
            } else {
                allCheckbox.checked = false;
            }
        }

        // 应用筛选
        function applyFilters() {
            // 首先隐藏所有字符分组
            document.querySelectorAll('[id^="char-"]').forEach(charDiv => {
                charDiv.style.display = 'none';
            });

            costumes.forEach(costume => {
                const matchesQuality = filters.quality.length === 0 || filters.quality.includes(costume.quality_name);
                const matchesCharacter = filters.character.length === 0 || filters.character.includes(costume.character);

                if (matchesQuality && matchesCharacter) {
                    costume.element.style.display = 'block';
                    // 显示对应的字符分组
                    const charDiv = costume.element.closest('[id^="char-"]');
                    if (charDiv) {
                        charDiv.style.display = 'flex';
                    }
                } else {
                    costume.element.style.display = 'none';
                }
            });

            // 更新字符导航栏
            updateCharacterNavigation();
        }
    } // 关闭initializeFilters函数
});

// 悬浮按钮组功能
const toggleButton = document.getElementById('toggleButton');
const buttonList = document.getElementById('buttonList');
const helpButton = document.getElementById('helpButton');
const contactButton = document.getElementById('contactButton');
const helpModal = document.getElementById('helpModal');
const contactModal = document.getElementById('contactModal');
const closeButtons = document.querySelectorAll('.closeModal');

// 展开/折叠按钮组
toggleButton.addEventListener('click', function () {
    buttonList.classList.toggle('hidden');
    // 切换箭头方向
    const svg = this.querySelector('svg path');
    if (buttonList.classList.contains('hidden')) {
        svg.setAttribute('d', 'M19 15l-7-7-7 7'); // 向上箭头（隐藏时显示向上，表示可展开）
    } else {
        svg.setAttribute('d', 'M19 9l-7 7-7-7'); // 向下箭头（显示时显示向下，表示可收起）
    }
});

// 打开帮助弹窗
helpButton.addEventListener('click', function () {
    helpModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // 防止背景滚动
});

// 打开联系我弹窗
contactButton.addEventListener('click', function () {
    contactModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // 防止背景滚动
});

// 关闭所有弹窗
function closeAllModals() {
    helpModal.classList.add('hidden');
    contactModal.classList.add('hidden');
    document.body.style.overflow = 'auto'; // 恢复滚动
}

// 为所有关闭按钮添加事件
closeButtons.forEach(button => {
    button.addEventListener('click', closeAllModals);
});

// 点击弹窗背景关闭
[helpModal, contactModal].forEach(modal => {
    modal.addEventListener('click', function (e) {
        if (e.target === this) {
            closeAllModals();
        }
    });
});

// ESC键关闭弹窗
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && (!helpModal.classList.contains('hidden') || !contactModal.classList.contains('hidden'))) {
        closeAllModals();
    }
})

// 加载动画控制
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.add('show');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('show');
}

// 表单提交处理
document.getElementById('searchForm').addEventListener('submit', function (e) {
    showLoading();

    // 确保最小显示时间0.5秒
    const startTime = Date.now();

    // 在实际提交前确保动画已显示
    setTimeout(() => {
        // 表单正常提交，这里不需要阻止默认行为
        // 因为我们希望表单正常提交到后端
    }, 100);
});

// 字符导航功能
window.scrollToCharacter = function (char) {
    const targetElement = document.getElementById('char-' + char);
    const resultsContainer = document.getElementById('resultsContainer');

    if (targetElement && resultsContainer) {
        // 计算目标元素在容器中的位置
        const containerRect = resultsContainer.getBoundingClientRect();
        const targetRect = targetElement.getBoundingClientRect();
        const scrollTop = resultsContainer.scrollTop;

        // 计算需要滚动的距离
        const targetScrollTop = scrollTop + (targetRect.top - containerRect.top) - 20; // 20px的偏移量

        // 平滑滚动到目标位置
        resultsContainer.scrollTo({
            top: targetScrollTop,
            behavior: 'smooth'
        });

        // 高亮显示目标字符
        highlightCharacter(char);
    }
};

// 高亮字符功能
function highlightCharacter(char) {
    // 移除所有现有的高亮
    document.querySelectorAll('.character-nav-btn').forEach(btn => {
        btn.classList.remove('bg-gradient-purple-blue', 'text-white');
        btn.classList.add('bg-white', 'text-gray-700');
    });

    // 高亮当前字符按钮
    const targetBtn = document.querySelector(`button[onclick="scrollToCharacter('${char}')"]`);
    if (targetBtn) {
        targetBtn.classList.remove('bg-white', 'text-gray-700');
        targetBtn.classList.add('bg-gradient-purple-blue', 'text-white');

        // 2秒后移除高亮
        setTimeout(() => {
            targetBtn.classList.remove('bg-gradient-purple-blue', 'text-white');
            targetBtn.classList.add('bg-white', 'text-gray-700');
        }, 2000);
    }
}

// 更新字符导航栏的可见性
function updateCharacterNavigation() {
    const navButtons = document.querySelectorAll('.character-nav-btn');
    const visibleChars = new Set();

    // 检查哪些字符当前可见
    document.querySelectorAll('[id^="char-"]').forEach(charDiv => {
        if (charDiv.style.display !== 'none') {
            const char = charDiv.id.replace('char-', '');
            visibleChars.add(char);
        }
    });

    // 更新导航按钮的可见性
    navButtons.forEach(btn => {
        const char = btn.textContent.trim();
        if (visibleChars.has(char)) {
            btn.style.display = 'inline-block';
        } else {
            btn.style.display = 'none';
        }
    });

    // 如果没有可见的字符，隐藏整个导航栏
    const navigationDiv = document.getElementById('characterNavigation');
    if (navigationDiv) {
        if (visibleChars.size === 0) {
            navigationDiv.style.display = 'none';
        } else {
            navigationDiv.style.display = 'block';
        }
    }
}