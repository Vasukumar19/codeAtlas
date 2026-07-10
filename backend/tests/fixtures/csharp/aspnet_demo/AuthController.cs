using Microsoft.AspNetCore.Mvc;

namespace Demo.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AuthController : ControllerBase
    {
        [HttpPost("login")]
        public IActionResult Login([FromBody] string username)
        {
            // FIXME: Use real auth
            return Ok(new { token = "fake-jwt" });
        }
    }
}
