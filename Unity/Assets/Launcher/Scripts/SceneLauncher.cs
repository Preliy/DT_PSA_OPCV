using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

namespace Preliy.Launcher
{
    [RequireComponent(typeof(UIDocument))]
    public class SceneLauncher : MonoBehaviour
    {
        [Serializable]
        public class SceneEntry
        {
            public string DisplayName;
            public string SceneName;
            [TextArea(2, 5)]
            public string Description;
        }

        [SerializeField]
        private List<SceneEntry> _scenes = new();

        private const string CARD_CLASS = "scene-card";
        private const string CARD_SELECTED_CLASS = "scene-card--selected";
        private const string CARD_UNAVAILABLE_CLASS = "scene-card--unavailable";

        private UIDocument _document;
        private VisualElement _list;
        private Label _detailTitle;
        private Label _detailDescription;
        private Button _startButton;
        private Button _quitButton;
        private VisualElement _loadingOverlay;
        private Label _loadingLabel;
        private ProgressBar _loadingProgress;

        private readonly List<Button> _cards = new();
        private int _selectedIndex = -1;
        private bool _isLoading;

        private void OnEnable()
        {
            _document = GetComponent<UIDocument>();
            var root = _document.rootVisualElement;

            _list = root.Q<VisualElement>("scene-list");
            _detailTitle = root.Q<Label>("detail-title");
            _detailDescription = root.Q<Label>("detail-description");
            _startButton = root.Q<Button>("start-button");
            _quitButton = root.Q<Button>("quit-button");
            _loadingOverlay = root.Q<VisualElement>("loading-overlay");
            _loadingLabel = root.Q<Label>("loading-label");
            _loadingProgress = root.Q<ProgressBar>("loading-progress");

            _startButton.clicked += StartSelected;
            _quitButton.clicked += Quit;
            root.RegisterCallback<KeyDownEvent>(OnKeyDown, TrickleDown.TrickleDown);

            _loadingOverlay.style.display = DisplayStyle.None;
            BuildCards();
            SelectFirstAvailable();
        }

        private void OnDisable()
        {
            if (_startButton != null) _startButton.clicked -= StartSelected;
            if (_quitButton != null) _quitButton.clicked -= Quit;
            _document?.rootVisualElement?.UnregisterCallback<KeyDownEvent>(OnKeyDown, TrickleDown.TrickleDown);
        }

        private void BuildCards()
        {
            _list.Clear();
            _cards.Clear();

            for (var i = 0; i < _scenes.Count; i++)
            {
                var index = i;
                var entry = _scenes[i];

                var card = new Button { focusable = true };
                card.AddToClassList(CARD_CLASS);

                var title = new Label(entry.DisplayName);
                title.AddToClassList("scene-card__title");
                card.Add(title);

                var sceneName = new Label(entry.SceneName);
                sceneName.AddToClassList("scene-card__scene");
                card.Add(sceneName);

                if (!IsAvailable(entry))
                {
                    card.AddToClassList(CARD_UNAVAILABLE_CLASS);
                    card.SetEnabled(false);
                    var tag = new Label("not in build");
                    tag.AddToClassList("scene-card__tag");
                    card.Add(tag);
                }

                card.clicked += () => Select(index);
                card.RegisterCallback<PointerDownEvent>(evt =>
                {
                    if (evt.clickCount == 2) StartScene(index);
                }, TrickleDown.TrickleDown);

                _list.Add(card);
                _cards.Add(card);
            }
        }

        private void SelectFirstAvailable()
        {
            var index = _scenes.FindIndex(IsAvailable);
            Select(index);
            if (index >= 0) _cards[index].Focus();
        }

        private void Select(int index)
        {
            _selectedIndex = index;

            for (var i = 0; i < _cards.Count; i++)
            {
                _cards[i].EnableInClassList(CARD_SELECTED_CLASS, i == index);
            }

            var valid = index >= 0 && index < _scenes.Count && IsAvailable(_scenes[index]);
            _detailTitle.text = valid ? _scenes[index].DisplayName : "No scene selected";
            _detailDescription.text = valid ? _scenes[index].Description : "Select a demo scene to start.";
            _startButton.SetEnabled(valid && !_isLoading);
        }

        private void OnKeyDown(KeyDownEvent evt)
        {
            if (_isLoading) return;

            switch (evt.keyCode)
            {
                case KeyCode.Return:
                case KeyCode.KeypadEnter:
                    StartSelected();
                    evt.StopPropagation();
                    break;
                case KeyCode.UpArrow:
                    MoveSelection(-1);
                    evt.StopPropagation();
                    break;
                case KeyCode.DownArrow:
                    MoveSelection(1);
                    evt.StopPropagation();
                    break;
            }
        }

        private void MoveSelection(int direction)
        {
            if (_scenes.Count == 0) return;

            var index = _selectedIndex;
            for (var step = 0; step < _scenes.Count; step++)
            {
                index = (index + direction + _scenes.Count) % _scenes.Count;
                if (!IsAvailable(_scenes[index])) continue;
                Select(index);
                _cards[index].Focus();
                return;
            }
        }

        private void StartSelected() => StartScene(_selectedIndex);

        private void StartScene(int index)
        {
            if (_isLoading || index < 0 || index >= _scenes.Count) return;
            var entry = _scenes[index];
            if (!IsAvailable(entry)) return;

            StartCoroutine(LoadScene(entry));
        }

        private IEnumerator LoadScene(SceneEntry entry)
        {
            _isLoading = true;
            _startButton.SetEnabled(false);
            _quitButton.SetEnabled(false);
            _list.SetEnabled(false);

            _loadingLabel.text = $"Loading {entry.DisplayName}…";
            _loadingProgress.value = 0f;
            _loadingOverlay.style.display = DisplayStyle.Flex;

            // Let the overlay render one frame before the load starts to stall the main thread
            yield return null;

            var operation = SceneManager.LoadSceneAsync(entry.SceneName, LoadSceneMode.Single);
            if (operation == null)
            {
                Debug.LogError($"Launcher: scene '{entry.SceneName}' could not be loaded");
                _isLoading = false;
                _loadingOverlay.style.display = DisplayStyle.None;
                _quitButton.SetEnabled(true);
                _list.SetEnabled(true);
                Select(_selectedIndex);
                yield break;
            }

            while (!operation.isDone)
            {
                // progress stops at 0.9 until activation; scale it to the full bar
                _loadingProgress.value = Mathf.Clamp01(operation.progress / 0.9f) * 100f;
                yield return null;
            }
        }

        private static bool IsAvailable(SceneEntry entry)
        {
            return !string.IsNullOrEmpty(entry.SceneName) && Application.CanStreamedLevelBeLoaded(entry.SceneName);
        }

        private static void Quit()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#endif
            Application.Quit();
        }
    }
}
