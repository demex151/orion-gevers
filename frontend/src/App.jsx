import {
  useEffect,
  useRef,
  useState,
} from "react";

import "./App.css";

const API = "http://127.0.0.1:8000";


// =========================================================
// UTILIDADES
// =========================================================

function sleep(ms) {
  return new Promise((resolve) =>
    setTimeout(resolve, ms)
  );
}


function cleanSubtitleText(text) {
  return String(text || "")
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/[*`#]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}


function createSubtitleChunks(text) {
  const clean =
    cleanSubtitleText(text);

  if (!clean) {
    return [];
  }

  const words =
    clean.split(" ");

  const chunks = [];

  let current = [];

  for (const word of words) {
    current.push(word);

    const line =
      current.join(" ");

    if (
      current.length >= 7 ||
      line.length >= 52
    ) {
      chunks.push(line);
      current = [];
    }
  }

  if (current.length) {
    chunks.push(
      current.join(" ")
    );
  }

  return chunks;
}


function normalizeCommand(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[.,!?¿¡]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}


function isEndCommand(text) {
  const value =
    normalizeCommand(text);

  return (
    value.includes(
      "termina la conversación"
    ) ||
    value.includes(
      "termina la conversacion"
    ) ||
    value.includes(
      "finaliza la conversación"
    ) ||
    value.includes(
      "finaliza la conversacion"
    ) ||
    value.includes(
      "gever termina la conversación"
    ) ||
    value.includes(
      "gever termina la conversacion"
    ) ||
    value.includes(
      "deja de escuchar"
    ) ||
    value.includes(
      "para de escuchar"
    ) ||
    value === "salir"
  );
}


// =========================================================
// MEMORIA
// =========================================================

function normalizeMemoryPayload(payload) {
  const raw =
    payload &&
    Object.prototype.hasOwnProperty.call(
      payload,
      "memories"
    )
      ? payload.memories
      : payload;

  if (raw == null) {
    return [];
  }

  const source =
    Array.isArray(raw)
      ? raw
      : typeof raw === "object"
        ? Object.entries(raw).map(
            ([key, value]) => ({
              key,
              value,
            })
          )
        : [raw];

  return source.map(
    (item, index) => {

      if (
        typeof item === "string" ||
        typeof item === "number"
      ) {

        return {
          id: `memory-${index}`,
          type: "MEMORIA",
          text: String(item),
          raw: item,
        };
      }


      if (
        item &&
        typeof item === "object" &&
        "key" in item &&
        "value" in item
      ) {

        const value =
          item.value;


        const valueText =
          typeof value === "string"
            ? value
            : value &&
                typeof value === "object"
              ? value.text ||
                value.content ||
                value.memory ||
                value.fact ||
                value.summary ||
                value.value ||
                JSON.stringify(
                  value,
                  null,
                  2
                )
              : String(
                  value ?? ""
                );


        return {
          id:
            `memory-${index}-${item.key}`,

          type:
            String(
              (
                value &&
                typeof value === "object" &&
                (
                  value.kind ||
                  value.type ||
                  value.category ||
                  value.tag
                )
              ) ||
              item.key ||
              "MEMORIA"
            ).toUpperCase(),

          text:
            String(valueText),

          raw:
            value,
        };
      }


      const text =
        item?.text ||
        item?.content ||
        item?.memory ||
        item?.fact ||
        item?.summary ||
        item?.value ||
        JSON.stringify(
          item,
          null,
          2
        );


      return {
        id:
          String(
            item?.id ||
            item?.memory_id ||
            `memory-${index}`
          ),

        type:
          String(
            item?.kind ||
            item?.type ||
            item?.category ||
            item?.tag ||
            "MEMORIA"
          ).toUpperCase(),

        text:
          String(text),

        raw:
          item,
      };
    }
  );
}


// =========================================================
// APP
// =========================================================

function App() {

  // =======================================================
  // REACT STATE
  // =======================================================

  const [
    message,
    setMessage
  ] = useState("");


  const [
    conversation,
    setConversation
  ] = useState([
    {
      sender: "GEVER",
      text:
        "Estoy listo. Puedes pulsar hablar o decir ORION.",
    },
  ]);


  const [
    status,
    setStatus
  ] = useState(
    "ESPERANDO"
  );


  const [
    conversationMode,
    setConversationMode
  ] = useState(false);


  const [
    isSending,
    setIsSending
  ] = useState(false);


  const [
    isListening,
    setIsListening
  ] = useState(false);


  const [
    subtitles,
    setSubtitles
  ] = useState([]);


  // =======================================================
  // NAVEGACIÓN + MEMORIA
  // =======================================================

  const [
    currentPage,
    setCurrentPage
  ] = useState(
    "inicio"
  );


  const [
    memories,
    setMemories
  ] = useState([]);


  const [
    memorySearch,
    setMemorySearch
  ] = useState("");


  const [
    memoryLoading,
    setMemoryLoading
  ] = useState(false);


  const [
    memoryError,
    setMemoryError
  ] = useState("");


  // =======================================================
  // REFERENCIAS
  // =======================================================

  const audioRef =
    useRef(null);


  const subtitleTimerRef =
    useRef(null);


  /*
    Un único modo controla todo:

    wake
    conversation
    stopped
  */
  const modeRef =
    useRef("wake");


  /*
    Evita dos controladores simultáneos.
  */
  const controllerRunningRef =
    useRef(false);


  const appAliveRef =
    useRef(true);


  // =======================================================
  // ARRANQUE
  // =======================================================

  useEffect(() => {

    appAliveRef.current =
      true;

    modeRef.current =
      "wake";


    const timer =
      setTimeout(() => {

        controllerLoop();

      }, 600);


    return () => {

      appAliveRef.current =
        false;

      modeRef.current =
        "stopped";

      clearTimeout(
        timer
      );

      stopCurrentAudio();
    };

  }, []);


  // =======================================================
  // CHAT VISUAL
  // =======================================================

  function addMessage(
    sender,
    text
  ) {

    setConversation(
      (current) => [
        ...current,
        {
          sender,
          text,
        },
      ]
    );
  }


  // =======================================================
  // MEMORIA
  // =======================================================

  async function loadMemories() {

    setMemoryLoading(
      true
    );

    setMemoryError(
      ""
    );


    try {

      const response =
        await fetch(
          `${API}/api/memories`,
          {
            method: "GET",
          }
        );


      if (!response.ok) {

        throw new Error(
          `Memoria respondió ${response.status}`
        );
      }


      const data =
        await response.json();


      if (
        data &&
        data.ok === false
      ) {

        throw new Error(
          data.error ||
          "No se pudo leer la memoria."
        );
      }


      setMemories(
        normalizeMemoryPayload(
          data
        )
      );

    } catch (error) {

      setMemoryError(
        error?.message ||
        "No se pudo cargar la memoria."
      );

    } finally {

      setMemoryLoading(
        false
      );
    }
  }


  function openPage(page) {

    setCurrentPage(
      page
    );


    if (
      page === "memoria"
    ) {

      loadMemories();
    }
  }


  const filteredMemories =
    memories.filter(
      (memory) => {

        const query =
          memorySearch
            .trim()
            .toLowerCase();


        if (!query) {
          return true;
        }


        return (
          String(
            memory.type || ""
          )
            .toLowerCase()
            .includes(query) ||

          String(
            memory.text || ""
          )
            .toLowerCase()
            .includes(query)
        );
      }
    );


  // =======================================================
  // SUBTÍTULOS
  // =======================================================

  function stopSubtitleTimer() {

    if (
      subtitleTimerRef.current
    ) {

      clearInterval(
        subtitleTimerRef.current
      );

      subtitleTimerRef.current =
        null;
    }
  }


  function stopCurrentAudio() {

    stopSubtitleTimer();


    if (
      audioRef.current
    ) {

      try {

        audioRef.current.pause();

      } catch {
        // Nada.
      }


      if (
        audioRef.current.src
      ) {

        try {

          URL.revokeObjectURL(
            audioRef.current.src
          );

        } catch {
          // Nada.
        }
      }


      audioRef.current =
        null;
    }


    setSubtitles([]);
  }


  function startRealSubtitles(
    text,
    audio
  ) {

    stopSubtitleTimer();


    const chunks =
      createSubtitleChunks(
        text
      );


    if (!chunks.length) {
      return;
    }


    const duration =
      Number.isFinite(
        audio.duration
      ) &&
      audio.duration > 0

        ? audio.duration

        : Math.max(
            2,
            text.split(" ").length /
              2.8
          );


    const intervalMs =
      Math.max(
        450,
        (
          duration * 1000
        ) /
          chunks.length
      );


    let index = 1;


    setSubtitles([
      chunks[0],
    ]);


    subtitleTimerRef.current =
      setInterval(() => {

        if (
          index >=
          chunks.length
        ) {

          stopSubtitleTimer();

          return;
        }


        setSubtitles(
          (previous) => [
            ...previous,
            chunks[index],
          ].slice(-2)
        );


        index += 1;

      }, intervalMs);
  }


  // =======================================================
  // TTS
  // =======================================================

  async function speakWithSubtitles(
    text
  ) {

    stopCurrentAudio();


    setStatus(
      "PREPARANDO_VOZ"
    );


    const response =
      await fetch(
        `${API}/api/tts`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify({
              text,
            }),
        }
      );


    if (!response.ok) {

      throw new Error(
        `TTS respondió ${response.status}`
      );
    }


    const blob =
      await response.blob();


    const url =
      URL.createObjectURL(
        blob
      );


    const audio =
      new Audio(url);


    audioRef.current =
      audio;


    return new Promise(
      (resolve, reject) => {

        let finished =
          false;


        function cleanup() {

          if (finished) {
            return;
          }


          finished =
            true;


          stopSubtitleTimer();


          setTimeout(
            () => {

              setSubtitles([]);

            },
            450
          );


          try {

            URL.revokeObjectURL(
              url
            );

          } catch {
            // Nada.
          }


          audioRef.current =
            null;
        }


        audio.addEventListener(
          "playing",

          () => {

            setStatus(
              "HABLANDO"
            );


            startRealSubtitles(
              text,
              audio
            );

          },

          {
            once: true,
          }
        );


        audio.addEventListener(
          "ended",

          () => {

            cleanup();

            resolve();

          },

          {
            once: true,
          }
        );


        audio.addEventListener(
          "error",

          () => {

            cleanup();

            reject(
              new Error(
                "No se pudo reproducir el audio."
              )
            );

          },

          {
            once: true,
          }
        );


        audio
          .play()
          .catch(
            (error) => {

              cleanup();

              reject(
                error
              );
            }
          );
      }
    );
  }


  // =======================================================
  // CHAT CON EL CEREBRO
  // =======================================================

  async function getGeverAnswer(
    userMessage
  ) {

    const cleanMessage =
      String(
        userMessage || ""
      ).trim();


    if (!cleanMessage) {

      return null;
    }


    addMessage(
      "TÚ",
      cleanMessage
    );


    setMessage("");

    setIsSending(
      true
    );

    setStatus(
      "PENSANDO"
    );

    setSubtitles([]);


    try {

      const response =
        await fetch(
          `${API}/api/chat`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify({
                message:
                  cleanMessage,
              }),
          }
        );


      if (!response.ok) {

        throw new Error(
          `Chat respondió ${response.status}`
        );
      }


      const data =
        await response.json();


      if (!data.ok) {

        throw new Error(
          data.error ||
          "GEVER no pudo responder."
        );
      }


      addMessage(
        "GEVER",
        data.answer
      );


      return data.answer;

    } finally {

      setIsSending(
        false
      );
    }
  }


  async function askAndSpeak(
    text
  ) {

    const answer =
      await getGeverAnswer(
        text
      );


    if (!answer) {
      return;
    }


    await speakWithSubtitles(
      answer
    );
  }


  // =======================================================
  // ESCUCHA NORMAL
  // =======================================================

  async function listenConversationTurn() {

    setIsListening(
      true
    );

    setStatus(
      "ESCUCHANDO"
    );

    setSubtitles([]);


    try {

      const response =
        await fetch(
          `${API}/api/listen`,
          {
            method: "POST",
          }
        );


      const data =
        await response.json();


      if (!data.ok) {

        throw new Error(
          data.error ||
          "No pude escucharte."
        );
      }


      return String(
        data.text || ""
      ).trim();

    } finally {

      setIsListening(
        false
      );
    }
  }


  // =======================================================
  // ESCUCHA WAKE WORD
  // =======================================================

  async function listenWakeWord() {

    const response =
      await fetch(
        `${API}/api/wake-listen`,
        {
          method: "POST",
        }
      );


    const data =
      await response.json();


    if (!data.ok) {

      return {
        activated: false,
        command: "",
      };
    }


    return {
      activated:
        Boolean(
          data.activated
        ),

      command:
        String(
          data.command || ""
        ).trim(),
    };
  }


  // =======================================================
  // ACTIVAR CONVERSACIÓN
  // =======================================================

  async function activateConversation(
    firstCommand = "",
    wakeActivation = false
  ) {

    modeRef.current =
      "conversation";


    setConversationMode(
      true
    );


    const command =
      String(
        firstCommand || ""
      ).trim();


    /*
      Si dijiste:

      ORION, dime la hora

      respondemos directamente.
    */

    if (command) {

      try {

        await askAndSpeak(
          command
        );

      } catch (error) {

        addMessage(
          "SISTEMA",
          `Error: ${error.message}`
        );
      }


      if (
        modeRef.current ===
        "conversation"
      ) {

        setStatus(
          "ESCUCHANDO"
        );
      }


      return;
    }


    /*
      Si solo dijiste:

      ORION

      GEVER confirma.
    */

    if (
      wakeActivation
    ) {

      addMessage(
        "GEVER",
        "Sí, te escucho."
      );


      try {

        await speakWithSubtitles(
          "Sí, te escucho."
        );

      } catch (error) {

        console.warn(
          "El navegador bloqueó o falló el saludo de activación:",
          error
        );
      }
    }


    if (
      modeRef.current ===
      "conversation"
    ) {

      setStatus(
        "ESCUCHANDO"
      );
    }
  }


  // =======================================================
  // FINALIZAR CONVERSACIÓN
  // =======================================================

  async function finishConversation(
    speakGoodbye = false
  ) {

    modeRef.current =
      "wake";


    setConversationMode(
      false
    );


    setIsListening(
      false
    );

    setSubtitles([]);


    stopCurrentAudio();


    if (
      speakGoodbye
    ) {

      try {

        await speakWithSubtitles(
          "Entendido. Conversación finalizada."
        );

      } catch {
        // El cierre continúa.
      }
    }


    setStatus(
      "ESPERANDO"
    );
  }


  // =======================================================
  // CONTROLADOR ÚNICO
  // =======================================================

  async function controllerLoop() {

    if (
      controllerRunningRef.current
    ) {

      return;
    }


    controllerRunningRef.current =
      true;


    try {

      while (
        appAliveRef.current
      ) {

        // =================================================
        // MODO WAKE
        // =================================================

        if (
          modeRef.current ===
          "wake"
        ) {

          setStatus(
            "ESPERANDO"
          );


          try {

            const wake =
              await listenWakeWord();


            if (
              !appAliveRef.current
            ) {

              break;
            }


            if (
              modeRef.current !==
              "wake"
            ) {

              continue;
            }


            if (
              !wake.activated
            ) {

              continue;
            }


            await sleep(
              180
            );


            await activateConversation(
              wake.command,
              true
            );


            continue;

          } catch (error) {

            console.error(
              "Wake error:",
              error
            );


            await sleep(
              500
            );


            continue;
          }
        }


        // =================================================
        // MODO CONVERSACIÓN
        // =================================================

        if (
          modeRef.current ===
          "conversation"
        ) {

          try {

            const heard =
              await listenConversationTurn();


            if (
              !appAliveRef.current
            ) {

              break;
            }


            if (
              modeRef.current !==
              "conversation"
            ) {

              continue;
            }


            if (!heard) {

              continue;
            }


            if (
              isEndCommand(
                heard
              )
            ) {

              await finishConversation(
                true
              );


              continue;
            }


            await askAndSpeak(
              heard
            );


            if (
              modeRef.current ===
              "conversation"
            ) {

              setStatus(
                "ESCUCHANDO"
              );
            }


            continue;

          } catch (error) {

            console.error(
              "Conversation error:",
              error
            );


            addMessage(
              "SISTEMA",
              `Error: ${error.message}`
            );


            if (
              modeRef.current ===
              "conversation"
            ) {

              setStatus(
                "ESCUCHANDO"
              );


              await sleep(
                500
              );
            }


            continue;
          }
        }


        await sleep(
          250
        );
      }

    } finally {

      controllerRunningRef.current =
        false;
    }
  }


  // =======================================================
  // BOTÓN PRINCIPAL
  // =======================================================

  async function toggleConversation() {

    if (
      modeRef.current ===
      "conversation"
    ) {

      await finishConversation(
        false
      );


      return;
    }


    modeRef.current =
      "conversation";


    setConversationMode(
      true
    );


    setStatus(
      "ESCUCHANDO"
    );
  }


  // =======================================================
  // CHAT ESCRITO
  // =======================================================

  async function sendMessage() {

    const clean =
      message.trim();


    if (
      !clean ||
      isSending
    ) {

      return;
    }


    try {

      await askAndSpeak(
        clean
      );


      if (
        modeRef.current ===
        "conversation"
      ) {

        setStatus(
          "ESCUCHANDO"
        );

      } else {

        setStatus(
          "ESPERANDO"
        );
      }

    } catch (error) {

      addMessage(
        "SISTEMA",
        `Error: ${error.message}`
      );


      setStatus(
        "ERROR"
      );
    }
  }


  function handleKeyDown(
    event
  ) {

    if (
      event.key ===
      "Enter"
    ) {

      event.preventDefault();

      sendMessage();
    }
  }


  // =======================================================
  // TEXTO DE ESTADO
  // =======================================================

  function statusText() {

    switch (status) {

      case "PENSANDO":
        return "PROCESANDO INSTRUCCIÓN";

      case "PREPARANDO_VOZ":
        return "PREPARANDO RESPUESTA";

      case "ESCUCHANDO":
        return "ESCUCHANDO";

      case "HABLANDO":
        return "RESPONDIENDO";

      case "ESPERANDO":
        return "ESPERANDO ORION";

      case "ERROR":
        return "CONEXIÓN INTERRUMPIDA";

      default:
        return "LISTO PARA TRABAJAR";
    }
  }


  // =======================================================
  // INTERFAZ
  // =======================================================

  return (

    <div className="gever-app">


      {/* ===================================================
          SIDEBAR
          =================================================== */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-icon">
            G
          </div>


          <div>

            <h1>
              GEVER
            </h1>

            <span>
              AI COMMAND SYSTEM
            </span>

          </div>

        </div>


        <nav className="navigation">

          <button
            className={
              `nav-item ${
                currentPage ===
                "inicio"
                  ? "active"
                  : ""
              }`
            }

            onClick={() =>
              openPage(
                "inicio"
              )
            }
          >

            <span>⌂</span>

            Inicio

          </button>


          <button className="nav-item">

            <span>◉</span>

            Conversaciones

          </button>


          <button
            className={
              `nav-item ${
                currentPage ===
                "memoria"
                  ? "active"
                  : ""
              }`
            }

            onClick={() =>
              openPage(
                "memoria"
              )
            }
          >

            <span>◇</span>

            Memoria

          </button>


          <button className="nav-item">

            <span>✓</span>

            Tareas

          </button>


          <button className="nav-item">

            <span>⬡</span>

            Agentes

          </button>

        </nav>


        <div className="sidebar-bottom">

          <button className="nav-item">

            <span>⚙</span>

            Configuración

          </button>


          <div className="system-mini">

            <div className="status-dot"></div>


            <div>

              <strong>
                Sistema operativo
              </strong>

              <span>
                Todos los sistemas activos
              </span>

            </div>

          </div>

        </div>

      </aside>


      {/* ===================================================
          MAIN
          =================================================== */}

      <main className="main">

        <header className="topbar">

          <div>

            <span className="eyebrow">

              {currentPage ===
              "memoria"

                ? "MEMORIA OPERATIVA"

                : "CENTRO DE OPERACIONES"}

            </span>


            <h2>

              {currentPage ===
              "memoria"

                ? "GEVER Memory Center"

                : "GEVER Command Center"}

            </h2>

          </div>


          <div className="top-status">

            <span className="live-dot"></span>

            GEVER ONLINE

          </div>

        </header>


        {/* =================================================
            INICIO
            ================================================= */}

        {currentPage ===
        "inicio" ? (


          <section className="dashboard">


            {/* ===============================================
                NÚCLEO
                =============================================== */}

            <section
              className={
                `gever-core-card state-${status.toLowerCase()}`
              }
            >

              <div className="core-background"></div>


              <div className="core-content">

                <span className="core-label">
                  INTELIGENCIA CENTRAL
                </span>


                <div className="ai-core">

                  <div className="orbit orbit-one"></div>

                  <div className="orbit orbit-two"></div>

                  <div className="orbit orbit-three"></div>

                  <div className="core-glow"></div>


                  <div className="core-center">
                    G
                  </div>

                </div>


                <h3>
                  GEVER
                </h3>


                <p className="core-status">

                  {statusText()}

                </p>


                <div
                  style={{
                    width: "100%",
                    maxWidth: "540px",
                    minHeight: "64px",
                    marginTop: "10px",
                    marginBottom: "8px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    gap: "5px",
                  }}
                >

                  {subtitles.map(
                    (
                      line,
                      index
                    ) => (

                      <div
                        key={
                          `${line}-${index}`
                        }

                        style={{
                          fontSize:
                            index ===
                            subtitles.length - 1
                              ? "15px"
                              : "13px",

                          fontWeight:
                            index ===
                            subtitles.length - 1
                              ? "600"
                              : "400",

                          color:
                            index ===
                            subtitles.length - 1
                              ? "#f3f7ff"
                              : "rgba(175,190,210,0.45)",

                          lineHeight:
                            "1.4",

                          transition:
                            "all 250ms ease",
                        }}
                      >

                        {line}

                      </div>

                    )
                  )}

                </div>


                {status !==
                "HABLANDO" && (

                  <p className="core-description">

                    {conversationMode

                      ? "Conversación continua activa. Habla normalmente; GEVER volverá a escucharte automáticamente."

                      : "Di ORION para comenzar una conversación o utiliza el botón."}

                  </p>

                )}


                <button
                  className="talk-button"

                  onClick={
                    toggleConversation
                  }
                >

                  <span className="mic-symbol">
                    ●
                  </span>


                  {conversationMode

                    ? status ===
                      "ESCUCHANDO"

                      ? "ESCUCHANDO..."

                      : status ===
                        "PENSANDO"

                        ? "PROCESANDO..."

                        : status ===
                          "PREPARANDO_VOZ"

                          ? "PREPARANDO VOZ..."

                          : status ===
                            "HABLANDO"

                            ? "GEVER HABLANDO"

                            : "FINALIZAR CONVERSACIÓN"

                    : "HABLAR CON GEVER"}

                </button>


                {conversationMode && (

                  <button
                    onClick={() =>
                      finishConversation(
                        false
                      )
                    }

                    style={{
                      marginTop: "10px",

                      background:
                        "transparent",

                      border:
                        "1px solid rgba(255,120,40,0.45)",

                      color:
                        "#ff9a4a",

                      borderRadius:
                        "10px",

                      padding:
                        "8px 16px",

                      cursor:
                        "pointer",
                    }}
                  >

                    FINALIZAR CONVERSACIÓN

                  </button>

                )}

              </div>

            </section>


            {/* ===============================================
                ACTIVIDAD
                =============================================== */}

            <aside className="right-panel">

              <div className="panel-title">

                <div>

                  <span className="eyebrow">
                    TIEMPO REAL
                  </span>

                  <h3>
                    Actividad
                  </h3>

                </div>


                <span className="live-indicator">
                  LIVE
                </span>

              </div>


              <div className="activity-list">


                <div className="activity">

                  <div className="activity-icon">
                    ✓
                  </div>


                  <div>

                    <strong>
                      Activación por voz
                    </strong>

                    <p>

                      {conversationMode

                        ? "Conversación continua activa."

                        : "Esperando ORION."}

                    </p>

                    <span>

                      {conversationMode

                        ? "ACTIVA"

                        : "WAKE WORD"}

                    </span>

                  </div>

                </div>


                <div className="activity">

                  <div className="activity-icon">
                    ◇
                  </div>


                  <div>

                    <strong>
                      Memoria conectada
                    </strong>

                    <p>
                      Memoria persistente disponible.
                    </p>

                    <span>
                      SISTEMA
                    </span>

                  </div>

                </div>


                <div className="activity">

                  <div className="activity-icon">
                    ◉
                  </div>


                  <div>

                    <strong>
                      Estado actual
                    </strong>

                    <p>
                      {statusText()}
                    </p>

                    <span>
                      {status}
                    </span>

                  </div>

                </div>

              </div>

            </aside>


            {/* ===============================================
                MÉTRICAS
                =============================================== */}

            <section className="metrics">


              <div className="metric-card">

                <div className="metric-top">

                  <span>
                    MEMORIA
                  </span>

                  <div className="metric-icon">
                    ◇
                  </div>

                </div>


                <strong>
                  ACTIVA
                </strong>

                <p>
                  Memoria persistente conectada
                </p>


                <div className="progress">

                  <div className="progress-fill memory-progress"></div>

                </div>

              </div>


              <div className="metric-card">

                <div className="metric-top">

                  <span>
                    CONVERSACIÓN
                  </span>

                  <div className="metric-icon">
                    ◉
                  </div>

                </div>


                <strong>

                  {conversationMode

                    ? "ACTIVA"

                    : "ESPERA"}

                </strong>


                <p>

                  {conversationMode

                    ? "Micrófono en modo continuo"

                    : "ORION disponible"}

                </p>


                <div className="progress">

                  <div
                    className="progress-fill task-progress"

                    style={{
                      width:
                        conversationMode
                          ? "100%"
                          : "30%",
                    }}
                  ></div>

                </div>

              </div>


              <div className="metric-card">

                <div className="metric-top">

                  <span>
                    MOTOR
                  </span>

                  <div className="metric-icon">
                    ⬡
                  </div>

                </div>


                <strong>
                  NEMOTRON
                </strong>


                <p>
                  Motor principal conectado
                </p>


                <div className="progress">

                  <div className="progress-fill agent-progress"></div>

                </div>

              </div>

            </section>


            {/* ===============================================
                CHAT
                =============================================== */}

            <section className="command-card">

              <div className="command-header">

                <div>

                  <span className="eyebrow">
                    COMUNICACIÓN DIRECTA
                  </span>

                  <h3>
                    Habla con GEVER
                  </h3>

                </div>


                <span className="secure">
                  ● CONEXIÓN LOCAL
                </span>

              </div>


              <div
                className="conversation"

                style={{
                  maxHeight: "280px",
                  overflowY: "auto",
                }}
              >

                <div
                  style={{
                    width: "100%",
                  }}
                >

                  {conversation.map(
                    (
                      item,
                      index
                    ) => (

                      <div
                        className="gever-message"

                        key={
                          `${item.sender}-${index}`
                        }

                        style={{
                          marginBottom:
                            "16px",
                        }}
                      >

                        <div className="message-avatar">

                          {item.sender ===
                          "TÚ"

                            ? "T"

                            : item.sender ===
                              "SISTEMA"

                              ? "!"

                              : "G"}

                        </div>


                        <div>

                          <span>
                            {item.sender}
                          </span>

                          <p>
                            {item.text}
                          </p>

                        </div>

                      </div>

                    )
                  )}

                </div>

              </div>


              <div className="command-input">

                <input
                  type="text"

                  value={
                    message
                  }

                  disabled={
                    isSending ||
                    isListening
                  }

                  placeholder={
                    isListening

                      ? "GEVER está escuchando..."

                      : isSending

                        ? "GEVER está trabajando..."

                        : "Escribe una instrucción para GEVER..."
                  }

                  onChange={
                    (event) =>
                      setMessage(
                        event.target.value
                      )
                  }

                  onKeyDown={
                    handleKeyDown
                  }
                />


                <button
                  className="voice-button"

                  onClick={
                    toggleConversation
                  }
                >

                  {conversationMode
                    ? "STOP"
                    : "MIC"}

                </button>


                <button
                  className="send-button"

                  onClick={
                    sendMessage
                  }

                  disabled={
                    isSending ||
                    isListening
                  }
                >

                  {isSending
                    ? "..."
                    : "ENVIAR"}

                </button>

              </div>

            </section>

          </section>


        ) : (


          /* ===============================================
             MEMORIA
             =============================================== */

          <section
            style={{
              padding: "28px",

              display:
                "flex",

              flexDirection:
                "column",

              gap:
                "22px",

              minHeight:
                "calc(100vh - 110px)",
            }}
          >


            {/* =============================================
                CABECERA
                ============================================= */}

            <div
              style={{
                display:
                  "flex",

                alignItems:
                  "center",

                justifyContent:
                  "space-between",

                gap:
                  "18px",

                flexWrap:
                  "wrap",
              }}
            >

              <div>

                <span className="eyebrow">
                  CONOCIMIENTO PERSISTENTE
                </span>


                <h2
                  style={{
                    margin:
                      "6px 0 0",

                    fontSize:
                      "30px",
                  }}
                >

                  Memoria de GEVER

                </h2>


                <p
                  style={{
                    margin:
                      "8px 0 0",

                    color:
                      "rgba(210,220,235,0.62)",

                    maxWidth:
                      "720px",
                  }}
                >

                  Consulta todo lo que GEVER tiene almacenado en su memoria persistente.

                </p>

              </div>


              <button
                className="talk-button"

                onClick={
                  loadMemories
                }

                disabled={
                  memoryLoading
                }

                style={{
                  width:
                    "auto",

                  minWidth:
                    "150px",

                  paddingLeft:
                    "20px",

                  paddingRight:
                    "20px",
                }}
              >

                {memoryLoading

                  ? "ACTUALIZANDO..."

                  : "ACTUALIZAR"}

              </button>

            </div>


            {/* =============================================
                CONTADORES
                ============================================= */}

            <div
              style={{
                display:
                  "grid",

                gridTemplateColumns:
                  "repeat(auto-fit, minmax(220px, 1fr))",

                gap:
                  "16px",
              }}
            >


              <div className="metric-card">

                <div className="metric-top">

                  <span>
                    MEMORIAS
                  </span>

                  <div className="metric-icon">
                    ◇
                  </div>

                </div>


                <strong>
                  {memories.length}
                </strong>


                <p>
                  Registros disponibles
                </p>

              </div>


              <div className="metric-card">

                <div className="metric-top">

                  <span>
                    RESULTADOS
                  </span>

                  <div className="metric-icon">
                    ⌕
                  </div>

                </div>


                <strong>
                  {filteredMemories.length}
                </strong>


                <p>
                  Coinciden con la búsqueda
                </p>

              </div>


              <div className="metric-card">

                <div className="metric-top">

                  <span>
                    ESTADO
                  </span>

                  <div className="metric-icon">
                    ✓
                  </div>

                </div>


                <strong>

                  {memoryError

                    ? "ERROR"

                    : memoryLoading

                      ? "LEYENDO"

                      : "CONECTADA"}

                </strong>


                <p>
                  Memoria persistente
                </p>

              </div>

            </div>


            {/* =============================================
                BUSCADOR + MEMORIAS
                ============================================= */}

            <section className="command-card">

              <div className="command-header">

                <div>

                  <span className="eyebrow">
                    BUSCADOR
                  </span>


                  <h3>
                    Buscar en la memoria
                  </h3>

                </div>


                <span className="secure">
                  ● MEMORIA LOCAL
                </span>

              </div>


              <div
                className="command-input"

                style={{
                  marginBottom:
                    "18px",
                }}
              >

                <input
                  type="text"

                  value={
                    memorySearch
                  }

                  placeholder=
                    "Escribe una palabra, negocio, decisión o dato..."

                  onChange={
                    (event) =>
                      setMemorySearch(
                        event.target.value
                      )
                  }
                />


                {memorySearch && (

                  <button
                    className="send-button"

                    onClick={() =>
                      setMemorySearch(
                        ""
                      )
                    }
                  >

                    LIMPIAR

                  </button>

                )}

              </div>


              {/* ===========================================
                  ERROR
                  =========================================== */}

              {memoryError && (

                <div
                  style={{
                    padding:
                      "16px",

                    borderRadius:
                      "12px",

                    border:
                      "1px solid rgba(255,120,40,0.35)",

                    background:
                      "rgba(255,120,40,0.07)",

                    color:
                      "#ffad6b",

                    marginBottom:
                      "16px",
                  }}
                >

                  {memoryError}

                </div>

              )}


              {/* ===========================================
                  CARGANDO
                  =========================================== */}

              {memoryLoading ? (

                <div
                  style={{
                    padding:
                      "38px 12px",

                    textAlign:
                      "center",

                    color:
                      "rgba(210,220,235,0.62)",
                  }}
                >

                  Leyendo la memoria de GEVER...

                </div>


              ) : filteredMemories.length ===
                0 ? (


                /* =========================================
                   SIN RESULTADOS
                   ========================================= */

                <div
                  style={{
                    padding:
                      "38px 12px",

                    textAlign:
                      "center",

                    color:
                      "rgba(210,220,235,0.62)",
                  }}
                >

                  {memories.length ===
                  0

                    ? "GEVER no devolvió memorias almacenadas."

                    : "No encontré recuerdos que coincidan con esa búsqueda."}

                </div>


              ) : (


                /* =========================================
                   TARJETAS DE MEMORIA
                   ========================================= */

                <div
                  style={{
                    display:
                      "grid",

                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(300px, 1fr))",

                    gap:
                      "14px",
                  }}
                >

                  {filteredMemories.map(
                    (memory) => (

                      <article
                        key={
                          memory.id
                        }

                        style={{
                          padding:
                            "18px",

                          borderRadius:
                            "14px",

                          border:
                            "1px solid rgba(80,145,255,0.18)",

                          background:
                            "rgba(7,15,29,0.62)",

                          boxShadow:
                            "inset 0 1px 0 rgba(255,255,255,0.025)",
                        }}
                      >

                        <div
                          style={{
                            display:
                              "flex",

                            justifyContent:
                              "space-between",

                            alignItems:
                              "center",

                            gap:
                              "12px",

                            marginBottom:
                              "12px",
                          }}
                        >

                          <span
                            style={{
                              fontSize:
                                "11px",

                              letterSpacing:
                                "0.14em",

                              color:
                                "#6ca9ff",

                              fontWeight:
                                "700",
                            }}
                          >

                            {memory.type}

                          </span>


                          <span
                            style={{
                              fontSize:
                                "11px",

                              color:
                                "rgba(210,220,235,0.38)",
                            }}
                          >

                            MEMORIA

                          </span>

                        </div>


                        <p
                          style={{
                            margin:
                              0,

                            whiteSpace:
                              "pre-wrap",

                            overflowWrap:
                              "anywhere",

                            color:
                              "rgba(236,243,255,0.88)",

                            lineHeight:
                              "1.6",

                            fontSize:
                              "14px",
                          }}
                        >

                          {memory.text}

                        </p>

                      </article>

                    )
                  )}

                </div>

              )}

            </section>

          </section>

        )}

      </main>

    </div>
  );
}


export default App;