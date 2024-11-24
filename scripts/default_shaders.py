DEFAULT_VERTEX_SHADER = '''
    #version 430 core

    in vec2 uvs;
    in vec2 in_vert;

    out vec2 frag_uvs;

    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        frag_uvs = uvs;
    }
'''

DEFAULT_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    void main() {
        f_color = vec4(frag_uvs.x, frag_uvs.y, 1.0, 0.0);
    }
'''

TEXTURE_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    uniform sampler2D tex;

    void main() {
        vec4 texture_color = texture(tex, frag_uvs);
        if (texture_color.a < 0.01) discard;
        f_color = texture_color;
    }
'''

PLAYER_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    uniform sampler2D tex;
    uniform bool hit;

    void main() {
        vec4 texture_color = texture(tex, frag_uvs);
        if (texture_color.a < 0.01) discard;
        if (hit) texture_color = vec4(0.733, 0.213, 0.213, 0.0);
        f_color = texture_color;
    }
'''

BACKGROUND_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    uniform sampler2D tex;
    uniform float t;

    void main() {
        vec2 uvs = frag_uvs;
        uvs.y += t * 0.25;

        vec4 texture_color = texture(tex, uvs);
        if (texture_color.a < 0.01) discard;
        f_color = texture_color;
    }
'''

FOREGROUND_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    uniform sampler2D tex;
    uniform float t;

    void main() {
        vec2 uvs = frag_uvs;
        uvs.y += t * 1.25;

        vec4 texture_color = texture(tex, uvs);
        if (texture_color.a < 0.01) discard;
        f_color = texture_color;
    }
'''

SCREEN_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    uniform sampler2D tex;
    uniform float chromatic_strength;
    uniform vec2 render_offset;

    float noise1(float x) {
        float y = fract(sin(x * 12.9898 + 78.233) * 43758.5453123) * 0.9 + 0.035;
        if (y < 0.1){
            return y;
        } else {
            return 0.1;
        }
    }

    vec2 barrel_distortion(vec2 uvs) {
        float r = distance(vec2(0.5), uvs);
        float distortion = 1.0 + 0.5 * r * r;
        vec2 distorted_uvs = vec2(0.5) + (uvs - vec2(0.5)) * distortion;
        return distorted_uvs;
    }

    void main() {

        vec2 blockUV = frag_uvs;

        float r = distance(vec2(0.5), blockUV);

        vec2 distorted_uvs = barrel_distortion(blockUV);

        distorted_uvs += render_offset;
        
        vec2 offset_red = vec2(-0.00175 * r * chromatic_strength, 0.0);
        vec2 offset_blue = vec2(0.00175 * r * chromatic_strength, 0.0);

        float color_red = texture(tex, distorted_uvs + offset_red).r;
        float color_green = texture(tex, distorted_uvs).g;
        float color_blue = texture(tex, distorted_uvs + offset_blue).b;

        if (distorted_uvs.x < 0.0 || distorted_uvs.y < 0.0 || distorted_uvs.x > 1.0 || distorted_uvs.y > 1.0) discard;

        vec4 texture_color = vec4(color_red, color_green, color_blue, 0.0);

        vec3 color;

        if (distorted_uvs.x < 0.005 || distorted_uvs.x > 0.995) {
            color = vec3(abs(noise1(r)) * 10.0);
        } else {
            color = vec3(abs(noise1(r)) * 10.0 * texture_color.r, abs(noise1(r)) * 10.0 * texture_color.g, abs(noise1(r)) * 10.0 * texture_color.b);
        }

        r = distance(vec2(0.5,0.3), blockUV);

        color = color * vec3((1.0 - r) * 1.25);

        f_color = vec4(color, 0.0);
    }

'''

ASTEROID_FRAGMENT_SHADER = '''
    #version 430 core

    in vec2 frag_uvs;

    out vec4 f_color;

    uniform sampler2D tex;
    uniform float rotation;

    void main() {
        float rotated_uv_x = (frag_uvs.x - 0.5) * cos(rotation) - (frag_uvs.y - 0.5) * sin(rotation);
        float rotated_uv_y = (frag_uvs.y - 0.5) * cos(rotation) + (frag_uvs.x - 0.5) * sin(rotation);

        vec2 rotated_uv = vec2(rotated_uv_x + 0.5, rotated_uv_y + 0.5);

        if (rotated_uv.x < 0.0 || rotated_uv.x > 1.0 || rotated_uv.y < 0.0 || rotated_uv.y > 1.0) {
            discard;
        }

        vec4 texture_color = texture(tex, rotated_uv);
        if (texture_color.a < 0.01) discard;
        f_color = texture_color;
    }
'''