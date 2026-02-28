

class BehavioralDataCollector {
    constructor() {
        this.keystrokes = [];
        this.mouseData = [];
        this.isCollecting = false;
        this.startTime = null;
        this.lastKeyTime = null;
        this.lastMousePosition = null;
    }

    startCollection() {
        this.isCollecting = true;
        this.keystrokes = [];
        this.mouseData = [];
        this.startTime = Date.now();
        this.lastKeyTime = null;
        this.lastMousePosition = null;
        
           document.addEventListener('keydown', this.handleKeyDown.bind(this));
           document.addEventListener('keyup', this.handleKeyUp.bind(this));
           document.addEventListener('mousemove', this.handleMouseMove.bind(this));
           document.addEventListener('click', this.handleClick.bind(this));
    }

    
    stopCollection() {
        this.isCollecting = false;
        
        document.removeEventListener('keydown', this.handleKeyDown.bind(this));
        document.removeEventListener('keyup', this.handleKeyUp.bind(this));
        document.removeEventListener('mousemove', this.handleMouseMove.bind(this));
        document.removeEventListener('click', this.handleClick.bind(this));
    }

    
    handleKeyDown(event) {
        if (!this.isCollecting) return;

        const currentTime = Date.now();
        let iki = null;

        if (this.lastKeyTime !== null) {
            iki = currentTime - this.lastKeyTime;
        }

        this.lastKeyTime = currentTime;

        this.keystrokes.push({
            timestamp: currentTime,
            key: event.key,
            code: event.code,
            iki: iki,
            keyCode: event.keyCode
        });
    }

    
    handleKeyUp(event) {
        if (!this.isCollecting) return;
        
    }

    
    handleMouseMove(event) {
        if (!this.isCollecting) return;

        const currentTime = Date.now();
        const currentPos = { x: event.clientX, y: event.clientY };

        if (this.lastMousePosition !== null) {
            const dx = currentPos.x - this.lastMousePosition.x;
            const dy = currentPos.y - this.lastMousePosition.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const timeDelta = currentTime - (this.mouseData[this.mouseData.length - 1]?.timestamp || this.startTime);
            const velocity = distance / Math.max(timeDelta, 1);

            this.mouseData.push({
                timestamp: currentTime,
                x: currentPos.x,
                y: currentPos.y,
                dx: dx,
                dy: dy,
                distance: distance,
                velocity: velocity
            });
        }

        this.lastMousePosition = currentPos;
    }

    
    handleClick(event) {
        if (!this.isCollecting) return;

        this.mouseData.push({
            timestamp: Date.now(),
            x: event.clientX,
            y: event.clientY,
            type: 'click',
            button: event.button
        });
    }

    
    extractFeatures() {
        const features = {};

        
        if (this.keystrokes.length > 0) {
            const ikis = this.keystrokes
                .filter(k => k.iki !== null)
                .map(k => k.iki);

            if (ikis.length > 0) {
                features.iki_mean = ikis.reduce((a, b) => a + b, 0) / ikis.length;
                features.iki_std = this.calculateStdDev(ikis);
                features.iki_min = Math.min(...ikis);
                features.iki_max = Math.max(...ikis);
                features.keystroke_rate = this.keystrokes.length / ((this.mouseData[this.mouseData.length - 1]?.timestamp || Date.now()) - this.startTime) * 1000;
            }

            features.total_keystrokes = this.keystrokes.length;
            features.unique_keys = new Set(this.keystrokes.map(k => k.key)).size;
        }

        
        if (this.mouseData.length > 0) {
            const velocities = this.mouseData
                .filter(m => m.velocity !== undefined)
                .map(m => m.velocity);

            if (velocities.length > 0) {
                features.mouse_velocity = velocities.reduce((a, b) => a + b, 0) / velocities.length;
                features.mouse_velocity_max = Math.max(...velocities);
            }

            const distances = this.mouseData
                .filter(m => m.distance !== undefined)
                .map(m => m.distance);

            if (distances.length > 0) {
                features.mouse_distance = distances.reduce((a, b) => a + b, 0);
                features.mouse_distance_mean = features.mouse_distance / distances.length;
            }

            const clicks = this.mouseData.filter(m => m.type === 'click').length;
            features.click_rate = clicks / ((Date.now() - this.startTime) / 1000);
        }

        
        if (this.mouseData.length > 2) {
            const accelerations = [];
            for (let i = 2; i < this.mouseData.length; i++) {
                const prev = this.mouseData[i - 1];
                const curr = this.mouseData[i];
                if (prev.velocity !== undefined && curr.velocity !== undefined) {
                    const accel = (curr.velocity - prev.velocity) / (curr.timestamp - prev.timestamp || 1);
                    accelerations.push(Math.abs(accel));
                }
            }
            if (accelerations.length > 0) {
                features.mouse_acceleration = accelerations.reduce((a, b) => a + b, 0) / accelerations.length;
            }
        }

        return features;
    }

    
    calculateStdDev(values) {
        if (values.length === 0) return 0;
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }

    
    getData() {
        return {
            keystrokes: this.keystrokes,
            mouseData: this.mouseData,
            features: this.extractFeatures(),
            duration: Date.now() - this.startTime
        };
    }

    
    clear() {
        this.keystrokes = [];
        this.mouseData = [];
        this.startTime = null;
        this.lastKeyTime = null;
        this.lastMousePosition = null;
    }
}

const behavioralCollector = new BehavioralDataCollector();
