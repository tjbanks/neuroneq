import click
import logging
import os

from .main import NeuronEQWindow

class DefaultCommandGroup(click.Group):
    """allow a default command for a group"""

    def command(self, *args, **kwargs):
        default_command = kwargs.pop('default_command', False)
        if default_command and not args:
            kwargs['name'] = kwargs.get('name', '<>')
        decorator = super(
            DefaultCommandGroup, self).command(*args, **kwargs)

        if default_command:
            def new_decorator(f):
                cmd = decorator(f)
                self.default_command = cmd.name
                return cmd

            return new_decorator

        return decorator

    def resolve_command(self, ctx, args):
        try:
            # test if the command parses
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.UsageError:
            # command did not parse, assume it is the default command
            args.insert(0, self.default_command)
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)

@click.group(cls=DefaultCommandGroup, invoke_without_command=True)
@click.option('--verbose', is_flag=True, default=False, help='Verbose printing')
@click.pass_context
def cli(ctx, verbose):
    if not ctx.invoked_subcommand:
        gui()

    if verbose:
        click.echo('Verbose printing mode is on.')

    ctx_obj = {}
    ctx_obj["verbose"] = verbose

    ctx.obj = ctx_obj


@cli.command('gui',help="Display Default GUI Window",default_command=True)
@click.pass_context
def gui(ctx):
    neq = NeuronEQWindow()
    neq.display()

if __name__ == "__main__":
    cli()