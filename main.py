from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from chatapp.agents import sentiment_agent, replier_agent, global_analyzer_agent
from chatapp.models import Context
from chatapp.memory.shorttermmemory import get_chats_from_memory, clear_memory, get_mood_shifts
from chatapp.memory.summarymemory import get_summaries
from datetime import datetime

console = Console()

class SentimentCLI:
    def __init__(self):
        self.context = Context(user_id="cli_user")
        self.sentiment_agent = None
        self.replier_agent = None
        self.global_analyzer = None
        self.session_start = datetime.now()
        self.message_count = 0
        # Clear mood        clear_mood_shifts()
        
    def initialize_agents(self):
        """Initialize the three agents."""
        console.print("[cyan]Initializing agents...[/cyan]")
        try:
            self.sentiment_agent = sentiment_agent
            self.replier_agent = replier_agent
            self.global_analyzer = global_analyzer_agent
            console.print("[green]✓ All agents initialized successfully![/green]\n")
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize agents: {e}[/red]")
            raise
    
    def show_banner(self):
        """Display welcome banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🤖  SENTIMENT ANALYSIS CHATBOT CLI  🤖                 ║
║                                                           ║
║   AI-Powered Conversations with Real-Time Sentiment      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
        console.print("\n[yellow]Type your message to chat, or use commands:[/yellow]")
        console.print("  [cyan]/help[/cyan]      - Show available commands")
        console.print("  [cyan]/memory[/cyan]    - Display current memory")
        console.print("  [cyan]/summaries[/cyan] - Show conversation summaries")
        console.print("  [cyan]/mood[/cyan]      - Display mood shifts")
        console.print("  [cyan]/stats[/cyan]     - Show conversation statistics")
        console.print("  [cyan]/clear[/cyan]     - Clear short-term memory")
        console.print("  [cyan]/exit[/cyan]      - End session\n")
    
    def show_help(self):
        """Display help information."""
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        
        table.add_row("/help", "Show this help message")
        table.add_row("/memory", "Display current short-term memory")
        table.add_row("/summaries", "Show all conversation summaries")
        table.add_row("/mood", "Display mood shifts and trends")
        table.add_row("/clear", "Clear short-term memory")
        table.add_row("/stats", "Show session statistics")
        table.add_row("/exit or /quit", "End session and show summary")
        
        console.print(table)
    
    def show_memory(self):
        """Display current short-term memory."""
        chats = get_chats_from_memory()
        
        if chats:
            console.print(f"\n[cyan]Short-Term Memory ({len(chats)}/5 slots):[/cyan]")
            for i, chat in enumerate(chats):
                sentiment_color = {
                    'POSITIVE': 'green',
                    'NEGATIVE': 'red',
                    'NEUTRAL': 'yellow'
                }.get(chat.sentiment_type, 'white')
                
                console.print(f"\n[bold]Message {i+1}:[/bold]")
                console.print(f"  [blue]User:[/blue] {chat.user}")
                console.print(f"  [green]Assistant:[/green] {chat.assistant}")
                console.print(f"  [bold]Sentiment:[/bold] [{sentiment_color}]{chat.sentiment_type}[/{sentiment_color}] ({chat.sentiment_score:.2f})")
        else:
            console.print("[yellow]Short-term memory is empty.[/yellow]")
    
    def show_summaries(self):
        """Display all conversation summaries."""
        summaries = get_summaries()
        
        if summaries:
            console.print(f"\n[cyan]Conversation Summaries ({len(summaries)}):[/cyan]")
            for i, summary in enumerate(summaries):
                panel = Panel(
                    f"[white]{summary.summary}[/white]\n\n"
                    f"[bold]Mood:[/bold] {summary.general_mood}\n"
                    f"[dim]Time: {summary.timestamp}[/dim]",
                    title=f"Summary {i+1}",
                    border_style="cyan"
                )
                console.print(panel)
        else:
            console.print("[yellow]No summaries available yet.[/yellow]")
    
    def show_mood_shifts(self):
        """Display mood shifts."""
        mood_shifts = get_mood_shifts()
        
        if mood_shifts:
            console.print(f"\n[cyan]Mood Shifts ({len(mood_shifts)}):[/cyan]")
            for i, shift in enumerate(mood_shifts):
                chats = shift.moodshift.chat
                if len(chats) >= 2:
                    before = chats[0]
                    after = chats[1]
                    
                    arrow = "📈" if after.sentiment_score > before.sentiment_score else "📉"
                    console.print(f"\n[bold]Shift {i+1}:[/bold] {arrow}")
                    console.print(f"  Before: [{before.sentiment_type}] {before.sentiment_score:.2f}")
                    console.print(f"  After:  [{after.sentiment_type}] {after.sentiment_score:.2f}")
        else:
            console.print("[yellow]No mood shifts detected yet.[/yellow]")
    
    def show_stats(self):
        """Display session statistics."""
        duration = datetime.now() - self.session_start
        chats = get_chats_from_memory()
        mood_shifts = get_mood_shifts()
        
        stats_table = Table(title="Session Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Session Duration", str(duration).split('.')[0])
        stats_table.add_row("Messages Exchanged", str(self.message_count))
        stats_table.add_row("Current Memory", f"{len(chats)}/5")
        stats_table.add_row("Mood Shifts", str(len(mood_shifts)))
        
        console.print(stats_table)
    
    def process_message(self, user_input: str):
        """Process user message and generate response."""
        self.message_count += 1
        
        console.print(f"\n[blue]You:[/blue] {user_input}")
        
        try:
            with console.status("[cyan]Analyzing sentiment...[/cyan]"):
                sentiment_result = self.sentiment_agent.invoke({
                    "messages": [{"role": "user", "content": f"Analyze the sentiment of this message and store it: {user_input}"}]
                })
            
            with console.status("[cyan]Generating response...[/cyan]"):
                response_result = self.replier_agent.invoke({
                    "messages": [{"role": "user", "content": user_input}]
                })
            
            response_text = "I apologize, but I couldn't generate a response."
            if isinstance(response_result, dict):
                if 'messages' in response_result:
                    for msg in reversed(response_result['messages']):
                        if hasattr(msg, 'type') and msg.type == 'ai':
                            if hasattr(msg, 'content'):
                                if isinstance(msg.content, list):
                                    text_parts = []
                                    for content_block in msg.content:
                                        if isinstance(content_block, dict) and 'text' in content_block:
                                            text_parts.append(content_block['text'])
                                    response_text = ''.join(text_parts)
                                else:
                                    response_text = str(msg.content)
                            break
                        elif hasattr(msg, 'role') and msg.role == 'assistant':
                            if hasattr(msg, 'content'):
                                if isinstance(msg.content, list):
                                    text_parts = []
                                    for content_block in msg.content:
                                        if isinstance(content_block, dict) and 'text' in content_block:
                                            text_parts.append(content_block['text'])
                                    response_text = ''.join(text_parts)
                                else:
                                    response_text = str(msg.content)
                            break
                elif 'output' in response_result:
                    response_text = response_result['output']
            
            sentiment_type = "NEUTRAL"
            sentiment_score = 0.5
            
            if isinstance(sentiment_result, dict) and 'output' in sentiment_result:
                output = sentiment_result['output']
                try:
                    if isinstance(output, str) and 'POSITIVE' in output:
                        sentiment_type = "POSITIVE"
                        import re
                        score_match = re.search(r"'score':\s*(-?\d+\.?\d*)", output)
                        if score_match:
                            sentiment_score = abs(float(score_match.group(1)))
                        else:
                            sentiment_score = 0.8
                    elif isinstance(output, str) and 'NEGATIVE' in output:
                        sentiment_type = "NEGATIVE"
                        import re
                        score_match = re.search(r"'score':\s*(-?\d+\.?\d*)", output)
                        if score_match:
                            sentiment_score = abs(float(score_match.group(1)))
                        else:
                            sentiment_score = 0.8
                    elif isinstance(output, dict):
                        sentiment_type = output.get('label', 'NEUTRAL').upper()
                        sentiment_score = abs(output.get('score', 0.5))
                except Exception:
                    if 'POSITIVE' in str(output):
                        sentiment_type = "POSITIVE"
                        sentiment_score = 0.8
                    elif 'NEGATIVE' in str(output):
                        sentiment_type = "NEGATIVE"
                        sentiment_score = 0.8
            
            sentiment_color = {
                'POSITIVE': 'green',
                'NEGATIVE': 'red',
                'NEUTRAL': 'yellow'
            }.get(sentiment_type, 'white')
            
            sentiment_emoji = {
                'POSITIVE': '😊',
                'NEGATIVE': '😢',
                'NEUTRAL': '😐'
            }.get(sentiment_type, '😐')
            
            console.print(f"\n[green]Assistant:[/green] {response_text}")
            console.print(f"[dim]Sentiment: [{sentiment_color}]{sentiment_emoji} {sentiment_type}[/{sentiment_color}] ({sentiment_score:.2f})[/dim]\n")
            
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
    
    def end_session(self):
        """End session and show summary."""
        console.print("\n[cyan]Ending session...[/cyan]\n")
        
        try:
            with console.status("[cyan]Generating session summary...[/cyan]"):
                summary_result = self.global_analyzer.invoke({
                    "messages": [{"role": "user", "content": "Provide a comprehensive summary of this conversation session."}]
                })
            
            if isinstance(summary_result, dict):
                if 'messages' in summary_result:
                    for msg in reversed(summary_result['messages']):
                        if hasattr(msg, 'type') and msg.type == 'ai':
                            if hasattr(msg, 'content'):
                                if isinstance(msg.content, list):
                                    text_parts = []
                                    for content_block in msg.content:
                                        if isinstance(content_block, dict) and 'text' in content_block:
                                            text_parts.append(content_block['text'])
                                    summary_text = ''.join(text_parts)
                                else:
                                    summary_text = str(msg.content)
                            break
                        elif hasattr(msg, 'role') and msg.role == 'assistant':
                            if hasattr(msg, 'content'):
                                if isinstance(msg.content, list):
                                    text_parts = []
                                    for content_block in msg.content:
                                        if isinstance(content_block, dict) and 'text' in content_block:
                                            text_parts.append(content_block['text'])
                                    summary_text = ''.join(text_parts)
                                else:
                                    summary_text = str(msg.content)
                            break
                elif 'output' in summary_result:
                    summary_text = summary_result['output']
            else:
                summary_text = str(summary_result)
            
            panel = Panel(
                summary_text,
                title="Session Summary",
                border_style="green"
            )
            console.print(panel)
            
        except Exception as e:
            console.print(f"[yellow]Could not generate summary: {e}[/yellow]")
        
        self.show_stats()
        console.print("\n[cyan]Thank you for using Sentiment Analysis Chatbot![/cyan]")
    
    def run(self):
        """Main CLI loop."""
        self.show_banner()
        self.initialize_agents()
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]>[/bold cyan]").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['/exit', '/quit']:
                    self.end_session()
                    break
                elif user_input.lower() == '/help':
                    self.show_help()
                elif user_input.lower() == '/memory':
                    self.show_memory()
                elif user_input.lower() == '/summaries':
                    self.show_summaries()
                elif user_input.lower() == '/mood':
                    self.show_mood_shifts()
                elif user_input.lower() == '/stats':
                    self.show_stats()
                elif user_input.lower() == '/clear':
                    clear_memory()
                    console.print("[green]✓ Short-term memory cleared![/green]")
                else:
                    self.process_message(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type /exit to end session properly.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


def main():
    try:
        cli = SentimentCLI()
        cli.run()
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")


if __name__ == "__main__":
    main()
